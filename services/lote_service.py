"""Registo do lote (RF04): lote, consumos e stock numa só transação (D-02, 
D-17, RN05, RN06)."""

from datetime import datetime

import psycopg

from domain.lote import DadosLoteInvalidos, Lote, StockInsuficiente
from repositories.lote_repository import LoteRepository
from repositories.materia_prima_repository import MateriaPrimaRepository
from repositories.movimento_stock_repository import MovimentoStockRepository
from repositories.produto_repository import ProdutoRepository
from repositories.receita_repository import ReceitaRepository


class LoteService:
    """Coordena o registo do lote e controla a transação."""

    def __init__(self, conn: psycopg.Connection, lotes: LoteRepository,
                 produtos: ProdutoRepository, receitas: ReceitaRepository,
                 materias: MateriaPrimaRepository, 
                 movimentos: MovimentoStockRepository):
        self.conn = conn
        self.lotes = lotes
        self.produtos = produtos
        self.receitas = receitas
        self.materias = materias
        self.movimentos = movimentos

    def registar_lote(self, id_produto: int, data_hora_producao: datetime,
                      turno: str, qtd_produzida: int, 
                      qtd_planeada: int | None = None) -> Lote:
        """Regista o lote e dá saída das matérias-primas; se faltar alguma, 
        não grava nada."""
        with self.conn.transaction():
            produto = self.produtos.obter(id_produto)
            if produto is None:
                raise DadosLoteInvalidos("O produto escolhido não existe.")

            # O domínio recusa um produto inativo, valida o lote e calcula
            # o código e a validade (RN08).
            lote = Lote.novo(produto, qtd_produzida=qtd_produzida,
                             turno=turno,
                             data_hora_producao=data_hora_producao,
                             qtd_planeada=qtd_planeada)

            linhas = self.receitas.listar_por_produto(id_produto)
            if not linhas:
                raise DadosLoteInvalidos(
                    f"O produto {produto.nome} ainda não tem receita.")

            # Lê e bloqueia as matérias-primas até ao fim da transação 
            # (FOR UPDATE, D-25).
            # As linhas vêm por ordem do id: duas transações bloqueiam sempre 
            # pela mesma ordem.
            necessidades = []
            for linha in linhas:
                materia = self.materias.obter_para_atualizar(
                    linha.id_materia_prima)
                consumo = linha.consumo_para(qtd_produzida, 
                                             produto.rendimento_lote)  # RN04
                necessidades.append((materia, consumo))

            # Cada falta: (nome, quantidade em falta, unidade), como pede a 
            # StockInsuficiente.
            faltas = [(m.nome, c - m.stock_atual, m.unidade)
                      for m, c in necessidades if not m.tem_stock(c)]
            if faltas:
                raise StockInsuficiente(faltas)

            lote = self.lotes.inserir(lote)
            for materia, consumo in necessidades:
                movimento = materia.registar_consumo(consumo, lote.id)
                self.movimentos.inserir(movimento)
                self.materias.somar_stock(materia.id, -movimento.quantidade)
        return lote
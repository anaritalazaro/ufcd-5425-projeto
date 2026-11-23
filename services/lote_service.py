"""Registo do lote (RF04): lote, consumos e stock numa só transação (D-02, 
D-17, RN05, RN06)."""

from datetime import date, datetime

import psycopg

from domain.lote import (DadosLoteInvalidos, FechoInvalido, Lote,
                         StockInsuficiente)
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

    def listar_do_dia(self, dia: date) -> list[Lote]:
        """RF15: os lotes produzidos num dia (abertos e fechados)."""
        return self.lotes.listar_do_dia(dia)

    def fechar_dia(self, dia: date,
                   quantidades: dict[int, tuple[int, int]]) -> list[Lote]:
        """RF07: fecha todos os lotes abertos do dia, ou nenhum.

        quantidades: id do lote → (vendido, desperdiçado).
        """
        with self.conn.transaction():
            # Bloqueia os lotes do dia: dois fechos ao mesmo tempo não
            # gravam por cima um do outro (como o FOR UPDATE do RF04, D-25).
            abertos = [lote for lote in
                       self.lotes.listar_do_dia(dia, para_atualizar=True)
                       if lote.estado == "aberto"]
            # Ficha do RF07: requer pelo menos um lote; o dia não pode
            # estar já fechado.
            if not abertos:
                raise DadosLoteInvalidos("Não há lotes abertos neste dia.")

            # Valida todos os lotes antes de gravar algum, para assinalar
            # todos os que falham (ficha do RF07).
            erros = {}
            for lote in abertos:
                if lote.id not in quantidades:
                    erros[lote.id] = "Indique o vendido e o desperdiçado."
                    continue
                try:
                    lote.fechar(*quantidades[lote.id])      # RN10
                except DadosLoteInvalidos as erro:
                    erros[lote.id] = str(erro)
            if erros:
                # Sai da transação com erro: nada é gravado.
                raise FechoInvalido(erros)

            for lote in abertos:
                self.lotes.fechar(lote)
        return abertos

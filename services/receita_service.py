"""Operações sobre as receitas (RF03). Sem páginas nesta versão: usado pelo script de dados."""

from decimal import Decimal

import psycopg

from domain.linha_receita import DadosReceitaInvalidos, LinhaReceita
from repositories.materia_prima_repository import MateriaPrimaRepository
from repositories.produto_repository import ProdutoRepository
from repositories.receita_repository import ReceitaRepository


class ReceitaService:
    """Coordena as receitas e controla as transações."""

    def __init__(self, conn: psycopg.Connection, receitas: ReceitaRepository,
                 produtos: ProdutoRepository, materias: MateriaPrimaRepository):
        self.conn = conn
        self.receitas = receitas
        self.produtos = produtos
        self.materias = materias

    def obter_receita(self, id_produto: int) -> list[LinhaReceita]:
        """Devolve as linhas da receita do produto."""
        return self.receitas.listar_por_produto(id_produto)

    def guardar_receita(self, id_produto: int, quantidades: dict[int, Decimal]) -> list[LinhaReceita]:
        """Grava a receita do produto: {id da matéria-prima: quantidade para o rendimento do lote}.

        O dicionário não deixa repetir a matéria-prima (RN03); a receita anterior é substituída.
        """
        if not quantidades:
            raise DadosReceitaInvalidos("A receita tem de ter pelo menos uma matéria-prima.")
        # O domínio valida cada quantidade (> 0, 3 casas).
        linhas = [LinhaReceita(id_produto=id_produto, id_materia_prima=id_mp,
                               quantidade_para_rendimento=qtd)
                  for id_mp, qtd in quantidades.items()]
        with self.conn.transaction():
            if self.produtos.obter(id_produto) is None:
                raise DadosReceitaInvalidos("O produto da receita não existe.")
            for linha in linhas:
                materia = self.materias.obter(linha.id_materia_prima)
                if materia is None or not materia.ativo:
                    raise DadosReceitaInvalidos("A receita indica uma matéria-prima inexistente ou inativa.")
            self.receitas.substituir(id_produto, linhas)
        return linhas
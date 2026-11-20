"""Acesso aos dados das receitas (tabela receita_ficha_tecnica)."""

import psycopg
from psycopg import errors

from domain.linha_receita import DadosReceitaInvalidos, LinhaReceita


#O ORDER BY id_materia_prima garante que o serviço do lote bloqueia as matérias-primas sempre pela mesma ordem.
SQL_LISTAR_POR_PRODUTO = """
    SELECT id_produto, id_materia_prima, quantidade_para_rendimento
    FROM receita_ficha_tecnica
    WHERE id_produto = %s
    ORDER BY id_materia_prima                                                                     
"""

SQL_APAGAR_DO_PRODUTO = "DELETE FROM receita_ficha_tecnica WHERE id_produto = %s"

SQL_INSERIR = """
    INSERT INTO receita_ficha_tecnica (id_produto, id_materia_prima, quantidade_para_rendimento)
    VALUES (%s, %s, %s)
"""


class ReceitaRepository:
    """Consultas e escritas na tabela receita_ficha_tecnica."""

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def listar_por_produto(self, id_produto: int) -> list[LinhaReceita]:
        """Devolve as linhas da receita de um produto, por ordem do id da matéria-prima."""
        linhas = self.conn.execute(SQL_LISTAR_POR_PRODUTO, (id_produto,)).fetchall()
        return [LinhaReceita(id_produto=l[0], id_materia_prima=l[1], quantidade_para_rendimento=l[2])
                for l in linhas]

    def substituir(self, id_produto: int, linhas: list[LinhaReceita]) -> None:
        """Substitui a receita do produto pelas linhas indicadas (a transação é do serviço)."""
        self.conn.execute(SQL_APAGAR_DO_PRODUTO, (id_produto,))
        for linha in linhas:
            try:
                self.conn.execute(SQL_INSERIR, (linha.id_produto, linha.id_materia_prima,
                                                linha.quantidade_para_rendimento))
            except errors.ForeignKeyViolation as erro:
                raise DadosReceitaInvalidos("A receita indica um produto ou uma matéria-prima que não existe.") from erro
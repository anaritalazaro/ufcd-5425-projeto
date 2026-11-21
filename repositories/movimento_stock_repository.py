"""Acesso aos dados dos movimentos de stock."""

import psycopg

from domain.movimento_stock import MovimentoStock

SQL_INSERIR = """
    INSERT INTO movimento_stock (id_materia_prima, tipo, quantidade, quantidade_contada, id_lote)
    VALUES (%(id_materia_prima)s, %(tipo)s, %(quantidade)s, %(quantidade_contada)s, %(id_lote)s)
    RETURNING id_movimento, data_hora
"""


class MovimentoStockRepository:
    """Escritas na tabela movimento_stock. Um movimento nunca se altera nem apaga."""

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def inserir(self, movimento: MovimentoStock) -> MovimentoStock:
        """Grava o movimento e devolve-o com o id e a data e hora dados pela base de dados."""
        parametros = {
            "id_materia_prima": movimento.id_materia_prima,
            "tipo": movimento.tipo,
            "quantidade": movimento.quantidade,
            "quantidade_contada": movimento.quantidade_contada,
            "id_lote": movimento.id_lote,
        }
        id_movimento, data_hora = self.conn.execute(SQL_INSERIR, parametros).fetchone()
        return movimento.com_registo(id_movimento, data_hora)
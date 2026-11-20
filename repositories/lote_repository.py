"""Acesso aos dados dos lotes de produção: tabela lote_producao."""

import psycopg
from psycopg import errors

from domain.lote import Lote, LoteJaRegistado

# id_equipamento e id_utilizador ficam vazios até às fases das temperaturas e da
# autenticação ([DD], schema.sql). A coluna chama-se lote no dicionário de dados e
# codigo_lote no diagrama de classes.
# Parâmetros com nome: os valores vão à parte do SQL (RNF05). [Sebenta 5425, 8.2]
SQL_INSERIR = """
    INSERT INTO lote_producao (id_produto, lote, data_hora_producao, turno,
                               qtd_planeada, qtd_produzida, validade, estado)
    VALUES (%(id_produto)s, %(codigo_lote)s, %(data_hora_producao)s, %(turno)s,
            %(qtd_planeada)s, %(qtd_produzida)s, %(validade)s, %(estado)s)
    RETURNING id_lote
"""


class LoteRepository:
    """Consultas e escritas na tabela lote_producao. Sem regras de negócio nem 
    transações."""

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def inserir(self, lote: Lote) -> Lote:
        """Grava um lote novo e devolve-o com o id atribuído pela base de dados."""
        parametros = {
            "id_produto": lote.id_produto,
            "codigo_lote": lote.codigo_lote,
            "data_hora_producao": lote.data_hora_producao,
            "turno": lote.turno,
            "qtd_planeada": lote.qtd_planeada,
            "qtd_produzida": lote.qtd_produzida,
            "validade": lote.validade,
            "estado": lote.estado,
        }
        try:
            linha = self.conn.execute(SQL_INSERIR, parametros).fetchone()
        except errors.UniqueViolation as erro:
            # O único UNIQUE da tabela é o código do lote: o mesmo lote outra 
            # vez (RN06).
            # [Sebenta 5425, 8 e 9.2; psycopg 3, errors]
            raise LoteJaRegistado(lote.codigo_lote) from erro
        lote.id = linha[0]
        return lote

"""Acesso aos dados dos lotes de produção: tabela lote_producao."""

from datetime import date

import psycopg
from psycopg import errors
from psycopg.rows import dict_row

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

# RF07, RF15: os lotes de um dia. "lote AS codigo_lote": a coluna chama-se
# lote no dicionário de dados e codigo_lote no diagrama (decisoes.md, 14).
# "AS id": o nome do argumento do Lote (como nos outros repositórios).
SQL_LISTAR_DO_DIA = """
    SELECT id_lote AS id, id_produto, lote AS codigo_lote,
           data_hora_producao, turno, qtd_planeada, qtd_produzida,
           qtd_vendida, qtd_desperdicada, validade, estado
    FROM lote_producao
    WHERE CAST(data_hora_producao AS DATE) = %s
    ORDER BY data_hora_producao, id_lote
"""

# O mesmo SELECT com FOR UPDATE: os lotes ficam bloqueados até ao fim da
# transação do fecho (como no RF04, D-25) [PostgreSQL, Explicit Locking].
SQL_LISTAR_DO_DIA_PARA_ATUALIZAR = SQL_LISTAR_DO_DIA + "    FOR UPDATE\n"

# RF07, RN10: o ck_lote_fecho volta a confirmar produzido = vendido +
# desperdiçado num lote fechado.
SQL_FECHAR = """
    UPDATE lote_producao
    SET qtd_vendida = %(qtd_vendida)s,
        qtd_desperdicada = %(qtd_desperdicada)s,
        estado = %(estado)s
    WHERE id_lote = %(id)s
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

    def listar_do_dia(self, dia: date, *,
                      para_atualizar: bool = False) -> list[Lote]:
        """Devolve os lotes produzidos num dia, por ordem de produção.

        Com para_atualizar=True, bloqueia-os até ao fim da transação; só
        tem efeito dentro de conn.transaction(), aberta pelo serviço.
        """
        sql = (SQL_LISTAR_DO_DIA_PARA_ATUALIZAR if para_atualizar
               else SQL_LISTAR_DO_DIA)
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, (dia,))
            return [Lote(**linha) for linha in cursor.fetchall()]

    def fechar(self, lote: Lote) -> None:
        """Grava o vendido, o desperdiçado e o estado de um lote fechado."""
        parametros = {
            "id": lote.id,
            "qtd_vendida": lote.qtd_vendida,
            "qtd_desperdicada": lote.qtd_desperdicada,
            "estado": lote.estado,
        }
        self.conn.execute(SQL_FECHAR, parametros)

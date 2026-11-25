"""Acesso aos dados das matérias-primas."""

from decimal import Decimal 

import psycopg
from psycopg import errors
from psycopg.rows import dict_row

from domain.materia_prima import MateriaPrima, NomeMateriaPrimaDuplicado

SQL_LISTAR = """
    SELECT id_materia_prima AS id, nome, unidade, stock_atual, stock_minimo,
           custo_unitario, alergenios, ativo
    FROM materia_prima
    ORDER BY nome
"""

SQL_OBTER = """
    SELECT id_materia_prima AS id, nome, unidade, stock_atual, stock_minimo,
           custo_unitario, alergenios, ativo
    FROM materia_prima
    WHERE id_materia_prima = %s
"""

# O mesmo SELECT com FOR UPDATE: a linha fica bloqueada até ao fim da transação (D-25).
# [Prop; PostgreSQL, Explicit Locking: Row-Level Locks]
SQL_OBTER_PARA_ATUALIZAR = SQL_OBTER + "    FOR UPDATE\n"

# Sem stock_atual: uma matéria-prima nova começa com o DEFAULT 0; o stock inicial é uma entrada.
SQL_CRIAR = """
    INSERT INTO materia_prima (nome, unidade, stock_minimo, custo_unitario, alergenios, ativo)
    VALUES (%(nome)s, %(unidade)s, %(stock_minimo)s, %(custo_unitario)s, %(alergenios)s, %(ativo)s)
    RETURNING id_materia_prima
"""

# Atualização relativa: o PostgreSQL soma sobre o valor que está gravado nesse momento,
# por isso duas entradas ao mesmo tempo não se perdem uma à outra. [Prop]
SQL_SOMAR_STOCK = """
    UPDATE materia_prima SET stock_atual = stock_atual + %s
    WHERE id_materia_prima = %s
    RETURNING stock_atual
"""


class MateriaPrimaRepository:
    """Consultas e escritas na tabela materia_prima."""

    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def listar(self) -> list[MateriaPrima]:
        """Devolve todas as matérias-primas, por ordem alfabética."""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(SQL_LISTAR)
            return [MateriaPrima(**linha) for linha in cursor.fetchall()]

    def obter(self, id_materia_prima: int) -> MateriaPrima | None:
        """Devolve a matéria-prima com este id, ou None se não existir."""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(SQL_OBTER, (id_materia_prima,))
            linha = cursor.fetchone()
        return MateriaPrima(**linha) if linha else None

    def obter_para_atualizar(self, id_materia_prima: int) -> MateriaPrima | None:
        """RF04: lê a matéria-prima e bloqueia a linha até ao fim da transação (D-25).

        Só tem efeito dentro de conn.transaction(): é o serviço do lote que a abre.
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(SQL_OBTER_PARA_ATUALIZAR, (id_materia_prima,))
            linha = cursor.fetchone()
        return MateriaPrima(**linha) if linha else None

    def existe_nome(self, nome: str) -> bool:
        """Diz se já existe uma matéria-prima com este nome (comparação exata)."""
        linha = self.conn.execute(
            "SELECT 1 FROM materia_prima WHERE nome = %s", (nome,)
        ).fetchone()
        return linha is not None

    def criar(self, materia: MateriaPrima) -> MateriaPrima:
        """Grava uma matéria-prima nova e devolve-a com o id atribuído."""
        parametros = {
            "nome": materia.nome,
            "unidade": materia.unidade,
            "stock_minimo": materia.stock_minimo,
            "custo_unitario": materia.custo_unitario,
            "alergenios": materia.alergenios,
            "ativo": materia.ativo,
        }
        try:
            linha = self.conn.execute(SQL_CRIAR, parametros).fetchone()
        except errors.UniqueViolation as erro:
            raise NomeMateriaPrimaDuplicado(materia.nome) from erro
        materia.id = linha[0]
        return materia

    def somar_stock(self, id_materia_prima: int, quantidade) -> Decimal:
        """Soma a quantidade ao stock atual (negativa num consumo ou num ajuste negativo).
        Devolve o stock gravado, com o RETURNING (sugestão do formador no PR #27).
        """
        linha = self.conn.execute(
            SQL_SOMAR_STOCK, (quantidade, id_materia_prima)).fetchone()
        return linha[0]
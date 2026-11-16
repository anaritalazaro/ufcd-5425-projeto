"""Acesso aos dados dos produtos: SQL parametrizado e conversão em objetos Produto."""

import psycopg
from psycopg import errors                           # O errors contém as exceções do PostgreSQL, uma por cada tipo de erro
from psycopg.rows import dict_row                    # O dict_row diz ao psycopg como devolver as linhas ()

from domain.produto import NomeProdutoDuplicado, Produto

# "AS id": a coluna fica com o nome do argumento do Produto. [Prop]
SQL_LISTAR = """
    SELECT id_produto AS id, nome, categoria, preco_venda, validade_horas,
           conservacao, ativo, rendimento_lote
    FROM produto
    ORDER BY nome
"""
# Parâmetros com nome: os valores vão à parte do SQL (RNF05). [Sebenta 5425, 8.2]
# RETURNING devolve o id gerado pelo SERIAL (no SQLite da sebenta: lastrowid).
SQL_CRIAR = """
    INSERT INTO produto (nome, categoria, preco_venda, validade_horas,
                         conservacao, ativo, rendimento_lote)
    VALUES (%(nome)s, %(categoria)s, %(preco_venda)s, %(validade_horas)s,
            %(conservacao)s, %(ativo)s, %(rendimento_lote)s)
    RETURNING id_produto
"""


class ProdutoRepository:
    """Consultas e escritas na tabela produto. Sem regras de negócio nem transações."""
    def __init__(self, conn: psycopg.Connection):
        # Recebe uma ligação já aberta; não escolhe a base de dados [Sebenta 5425, 8.2].
        self.conn = conn

    def listar(self) -> list[Produto]:
        """Devolve todos os produtos, por ordem alfabética do nome."""
        # dict_row: cada linha vem como dicionário, e Produto(**linha) cria o objeto.
        # Os dados lidos passam outra vez pelos setters do Produto. [Prop]
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(SQL_LISTAR)
            return [Produto(**linha) for linha in cursor.fetchall()]

    def criar(self, produto: Produto) -> Produto:
        """Grava um produto novo e devolve-o com o id atribuído pela base de dados."""
        parametros = {
            "nome": produto.nome,
            "categoria": produto.categoria,
            "preco_venda": produto.preco_venda,
            "validade_horas": produto.validade_horas,
            "conservacao": produto.conservacao,
            "ativo": produto.ativo,
            "rendimento_lote": produto.rendimento_lote,
        }
        try:
            linha = self.conn.execute(SQL_CRIAR, parametros).fetchone()
        except errors.UniqueViolation as erro:
            # O único UNIQUE da tabela é o nome; traduz o erro técnico numa exceção do domínio [Sebenta 5425, 8 e 9.2].
            raise NomeProdutoDuplicado(produto.nome) from erro
        produto.id = linha[0]
        return produto

    def existe_nome(self, nome: str) -> bool:
        """Diz se já existe um produto com este nome (comparação exata)."""
        linha = self.conn.execute(
            "SELECT 1 FROM produto WHERE nome = %s", (nome,)
        ).fetchone()
        return linha is not None
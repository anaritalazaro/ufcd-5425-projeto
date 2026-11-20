"""Operações sobre produtos: coordena o domínio e o repositório."""

import psycopg

from domain.produto import NomeProdutoDuplicado, Produto
from repositories.produto_repository import ProdutoRepository


class ProdutoService:
    """Coordena as operações dos produtos e controla as transações."""

    def __init__(self, conn: psycopg.Connection, repository: ProdutoRepository):
        # Recebe a ligação porque é o serviço que decide onde a transação começa e acaba (decisão da Sessão 6) [Sebenta 5425, 9.1].
        self.conn = conn
        self.repository = repository

    def listar_produtos(self) -> list[Produto]:
        """Devolve todos os produtos."""
        return self.repository.listar()

    def criar_produto(self, **dados) -> Produto:
        """Valida e grava um produto novo; recusa um nome repetido (RN01)."""
        # A validação dos dados acontece aqui, nos setters do Produto.
        produto = Produto(**dados)
        with self.conn.transaction():
            # 1.º proteção: pergunta antes de gravar, para mostrar uma mensagem clara.
            # 2.º proteção: se dois pedidos gravarem ao mesmo tempo, as duas perguntas dizem "não existe"; o UNIQUE recusa o segundo [Sebenta 5425, 9.2].
            if self.repository.existe_nome(produto.nome):
                raise NomeProdutoDuplicado(produto.nome)
            return self.repository.criar(produto)
        
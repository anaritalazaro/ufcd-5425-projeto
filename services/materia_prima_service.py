"""Operações sobre matérias-primas e stock."""

from decimal import Decimal

import psycopg

from domain.materia_prima import DadosMateriaPrimaInvalidos, MateriaPrima, NomeMateriaPrimaDuplicado
from domain.movimento_stock import MovimentoStock
from repositories.materia_prima_repository import MateriaPrimaRepository
from repositories.movimento_stock_repository import MovimentoStockRepository


class MateriaPrimaService:
    """Coordena as matérias-primas e o stock, e controla as transações."""

    def __init__(self, conn: psycopg.Connection, materias: MateriaPrimaRepository,
                 movimentos: MovimentoStockRepository):
        self.conn = conn
        self.materias = materias
        self.movimentos = movimentos

    def listar_materias_primas(self) -> list[MateriaPrima]:
        """Devolve todas as matérias-primas."""
        return self.materias.listar()

    def criar_materia_prima(self, **dados) -> MateriaPrima:
        """Valida e grava uma matéria-prima nova, com stock 0; recusa um nome repetido (RN01)."""
        materia = MateriaPrima(**dados)
        with self.conn.transaction():
            # Consulta antecipada para a mensagem clara; o UNIQUE protege o caso concorrente [Sebenta 5425, 9.2].
            if self.materias.existe_nome(materia.nome):
                raise NomeMateriaPrimaDuplicado(materia.nome)
            return self.materias.criar(materia)

    def registar_entrada(self, id_materia_prima: int, quantidade: Decimal) -> MovimentoStock:
        """Regista uma entrada: grava o movimento e soma ao stock, na mesma transação (D-02)."""
        with self.conn.transaction():
            materia = self.materias.obter(id_materia_prima)
            if materia is None:
                raise DadosMateriaPrimaInvalidos("A matéria-prima escolhida não existe.")
            # O domínio valida a quantidade e cria o movimento.
            movimento = materia.registar_entrada(quantidade)
            movimento = self.movimentos.inserir(movimento)
            self.materias.somar_stock(materia.id, movimento.quantidade)
        return movimento
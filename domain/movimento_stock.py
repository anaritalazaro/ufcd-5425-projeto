"""Movimento de stock: entrada, ajuste ou consumo de uma matéria-prima (RN06, RN07)."""

from datetime import datetime
from decimal import Decimal

from domain.validacao import decimal_validado

TIPOS_MOVIMENTO = ("entrada", "ajuste", "consumo")
MAX_QUANTIDADE = Decimal("1000000000")  # DECIMAL(12,3)


class DadosMovimentoInvalidos(ValueError):
    """Um dado do movimento de stock tem um valor inválido."""

class MovimentoStock:
    """Registo histórico de stock. Só de leitura: um movimento nunca se altera. [Sebenta 5425, 6.2]"""

    def __init__(self, *, id_materia_prima, tipo, quantidade, quantidade_contada=None,
                 id_lote=None, data_hora=None, id=None):
        if type(id_materia_prima) is not int or id_materia_prima <= 0:
            raise TypeError("O movimento precisa do id de uma matéria-prima gravada.")
        if type(tipo) is not str:
            raise TypeError("O tipo do movimento tem de ser texto.")
        if tipo not in TIPOS_MOVIMENTO:
            raise DadosMovimentoInvalidos(
                f"O tipo tem de ser um de: {', '.join(TIPOS_MOVIMENTO)}."
            )

        # Quantidade: entrada e consumo positivos; no ajuste, a diferença, nunca 0. [ck_movimento_quantidade]
        if tipo == "ajuste":
            if type(quantidade) is not Decimal:
                raise TypeError("O campo quantidade tem de ser Decimal.")
            if quantidade == 0:
                raise DadosMovimentoInvalidos("Um ajuste tem de alterar o stock.")
            
            # Valida o valor absoluto e repõe o sinal da quantidade original.
            quantidade = decimal_validado(abs(quantidade), "quantidade", 3, MAX_QUANTIDADE,
                                 DadosMovimentoInvalidos).copy_sign(quantidade)

        else:
            quantidade = decimal_validado(quantidade, "quantidade", 3, MAX_QUANTIDADE,
                                          DadosMovimentoInvalidos, positivo=True)

        # Quantidade contada: obrigatória no ajuste e vazia nos outros. [ck_movimento_contada]
        if tipo == "ajuste":

            if quantidade_contada is None:
                raise DadosMovimentoInvalidos("Um ajuste tem de indicar a quantidade contada.")

            quantidade_contada = decimal_validado(quantidade_contada, "quantidade_contada", 3,
                                                  MAX_QUANTIDADE, DadosMovimentoInvalidos)
        elif quantidade_contada is not None:
            raise DadosMovimentoInvalidos("Só o ajuste tem quantidade contada.")

        # Lote: obrigatório no consumo e vazio nos outros. [ck_movimento_lote]
        if tipo == "consumo":
            if type(id_lote) is not int or id_lote <= 0:
                raise DadosMovimentoInvalidos("Um consumo tem de indicar o lote.")
        elif id_lote is not None:
            raise DadosMovimentoInvalidos("Só o consumo está associado a um lote.")

        if data_hora is not None and type(data_hora) is not datetime:
            raise TypeError("A data e hora tem de ser datetime.")

        self._id = id
        self._id_materia_prima = id_materia_prima
        self._tipo = tipo
        self._quantidade = quantidade
        self._quantidade_contada = quantidade_contada
        self._id_lote = id_lote
        self._data_hora = data_hora

    # Só getters: sem setters, os atributos não se alteram depois de criados.
    @property
    def id(self): return self._id
    @property
    def id_materia_prima(self): return self._id_materia_prima
    @property
    def tipo(self): return self._tipo
    @property
    def quantidade(self): return self._quantidade
    @property
    def quantidade_contada(self): return self._quantidade_contada
    @property
    def id_lote(self): return self._id_lote
    @property
    def data_hora(self): return self._data_hora

    def com_registo(self, id: int, data_hora: datetime) -> "MovimentoStock":
        """Devolve uma cópia com o id e a data e hora atribuídos pela base de dados."""
        return MovimentoStock(id_materia_prima=self._id_materia_prima, tipo=self._tipo,
                              quantidade=self._quantidade,
                              quantidade_contada=self._quantidade_contada,
                              id_lote=self._id_lote, data_hora=data_hora, id=id)

    def efeito_no_stock(self, stock: Decimal) -> Decimal:
        """Devolve o stock depois deste movimento (diagrama de classes v2)."""
        if self._tipo == "consumo":
            return stock - self._quantidade
        return stock + self._quantidade  # entrada soma; ajuste soma a diferença (positiva ou negativa)
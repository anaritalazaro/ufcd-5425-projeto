"""Linha da receita (ficha técnica): quantidade de uma matéria-prima para o rendimento do lote (RF03, RN04)."""

from decimal import ROUND_UP, Decimal

from domain.movimento_stock import MAX_QUANTIDADE
from domain.validacao import decimal_validado


class DadosReceitaInvalidos(ValueError):
    """Um dado da receita tem um valor inválido."""


class LinhaReceita:
    """Uma linha da receita de um produto. Resolve a relação N:M entre produto e matéria-prima."""

    def __init__(self, *, id_produto, id_materia_prima, quantidade_para_rendimento):
        if type(id_produto) is not int or id_produto <= 0:
            raise TypeError("A linha da receita precisa do id de um produto gravado.")
        if type(id_materia_prima) is not int or id_materia_prima <= 0:
            raise TypeError("A linha da receita precisa do id de uma matéria-prima gravada.")
        self._id_produto = id_produto
        self._id_materia_prima = id_materia_prima

        # DECIMAL(12,3) e CHECK(> 0) no schema.sql (ck_receita_quantidade)
        self._quantidade_para_rendimento = decimal_validado(
            quantidade_para_rendimento, "quantidade_para_rendimento", 3, MAX_QUANTIDADE,
            DadosReceitaInvalidos, positivo=True)

    @property
    def id_produto(self) -> int:
        return self._id_produto

    @property
    def id_materia_prima(self) -> int:
        return self._id_materia_prima

    @property
    def quantidade_para_rendimento(self) -> Decimal:
        return self._quantidade_para_rendimento

    def consumo_para(self, qtd_produzida: int, rendimento_lote: int) -> Decimal:
        """RN04: consumo = quantidade na receita × (quantidade produzida ÷ rendimento do lote)."""
        if type(qtd_produzida) is not int or type(rendimento_lote) is not int:
            raise TypeError("A quantidade produzida e o rendimento têm de ser inteiros.")
        if qtd_produzida <= 0 or rendimento_lote <= 0:
            raise DadosReceitaInvalidos("A quantidade produzida e o rendimento têm de ser maiores do que zero.")
        
        # Multiplica antes de dividir, para só arredondar uma vez.
        consumo = self._quantidade_para_rendimento * qtd_produzida / rendimento_lote
        
        # 3 casas, como a coluna; arredonda para cima, para nunca dar 0 nem consumir a menos.
        return consumo.quantize(Decimal("0.001"), rounding=ROUND_UP)
from decimal import Decimal

import pytest

from domain.movimento_stock import DadosMovimentoInvalidos, MovimentoStock


def test_entrada_valida():
    movimento = MovimentoStock(id_materia_prima=1, tipo="entrada", quantidade=Decimal("500"))
    assert movimento.efeito_no_stock(Decimal("100")) == Decimal("600.000")


@pytest.mark.parametrize("dados", [
    {"tipo": "entrada", "quantidade": Decimal("0")},
    {"tipo": "entrada", "quantidade": Decimal("1"), "id_lote": 5},
    {"tipo": "consumo", "quantidade": Decimal("1")},
    {"tipo": "ajuste", "quantidade": Decimal("-2")},
    {"tipo": "ajuste", "quantidade": Decimal("0"), "quantidade_contada": Decimal("10")},
    {"tipo": "devolucao", "quantidade": Decimal("1")},
])
def test_regras_do_schema(dados):
    with pytest.raises(DadosMovimentoInvalidos):
        MovimentoStock(id_materia_prima=1, **dados)


def test_consumo_e_ajuste_no_stock():
    consumo = MovimentoStock(id_materia_prima=1, tipo="consumo", quantidade=Decimal("30"), id_lote=7)
    ajuste = MovimentoStock(id_materia_prima=1, tipo="ajuste", quantidade=Decimal("-2"),
                            quantidade_contada=Decimal("68"))
    assert consumo.efeito_no_stock(Decimal("100")) == Decimal("70.000")
    assert ajuste.efeito_no_stock(Decimal("70")) == Decimal("68.000")


def test_movimento_so_de_leitura():
    movimento = MovimentoStock(id_materia_prima=1, tipo="entrada", quantidade=Decimal("1"))
    with pytest.raises(AttributeError):
        movimento.quantidade = Decimal("2")
from decimal import Decimal

import pytest

from domain.materia_prima import DadosMateriaPrimaInvalidos, MateriaPrima
from domain.movimento_stock import DadosMovimentoInvalidos


def dados(**alteracoes):
    base = {"nome": "Farinha T65", "unidade": "g", "custo_unitario": Decimal("0.00085"),
            "stock_minimo": Decimal("5000")}
    base.update(alteracoes)
    return base


def test_cria_com_stock_zero():
    materia = MateriaPrima(**dados())
    assert materia.stock_atual == Decimal("0.000")
    assert materia.custo_unitario == Decimal("0.000850")
    assert materia.alergenios is None


def test_alergenios_vazio_fica_none():
    assert MateriaPrima(**dados(alergenios="  ")).alergenios is None


@pytest.mark.parametrize("campo, valor", [
    ("unidade", None), ("custo_unitario", 0.5), ("stock_minimo", 10), ("ativo", 1),
])
def test_tipo_errado_da_type_error(campo, valor):
    with pytest.raises(TypeError):
        MateriaPrima(**dados(**{campo: valor}))


@pytest.mark.parametrize("campo, valor", [
    ("nome", " "), ("unidade", "kg"), ("custo_unitario", Decimal("-0.01")),
    ("custo_unitario", Decimal("0.0000001")), ("stock_minimo", Decimal("-1")),
    ("stock_minimo", Decimal("1.0001")),
])
def test_valor_invalido_da_value_error(campo, valor):
    with pytest.raises(DadosMateriaPrimaInvalidos):
        MateriaPrima(**dados(**{campo: valor}))


def test_stock_atual_nao_tem_setter():
    materia = MateriaPrima(**dados())
    with pytest.raises(AttributeError):
        materia.stock_atual = Decimal("100")


def test_registar_entrada_soma_ao_stock():
    materia = MateriaPrima(**dados(id=1))
    movimento = materia.registar_entrada(Decimal("25000"))
    assert materia.stock_atual == Decimal("25000.000")
    assert movimento.tipo == "entrada"
    assert movimento.id_materia_prima == 1


def test_entrada_invalida_mantem_o_stock():
    materia = MateriaPrima(**dados(id=1, stock_atual=Decimal("100")))
    with pytest.raises(DadosMovimentoInvalidos):
        materia.registar_entrada(Decimal("0"))
    assert materia.stock_atual == Decimal("100.000")


def test_tem_stock_e_abaixo_do_minimo():
    materia = MateriaPrima(**dados(stock_atual=Decimal("1000")))
    assert materia.tem_stock(Decimal("1000"))
    assert not materia.tem_stock(Decimal("1000.001"))
    assert materia.abaixo_do_minimo()


def test_registar_consumo_desconta_o_stock():
    materia = MateriaPrima(**dados(id=1, stock_atual=Decimal("25000")))
    movimento = materia.registar_consumo(Decimal("903"), id_lote=1)
    assert materia.stock_atual == Decimal("24097.000")      # critério do RF04
    assert movimento.tipo == "consumo"
    assert movimento.id_lote == 1


def test_consumo_sem_stock_e_recusado_e_mantem_o_stock():
    materia = MateriaPrima(**dados(id=1, stock_atual=Decimal("100")))
    with pytest.raises(DadosMateriaPrimaInvalidos):
        materia.registar_consumo(Decimal("100.001"), id_lote=1)
    assert materia.stock_atual == Decimal("100.000")
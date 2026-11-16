from decimal import Decimal

import pytest

from domain.produto import DadosProdutoInvalidos, Produto


def dados(**alteracoes):
    base = {
        "nome": "Pastel de nata",
        "categoria": "Pastelaria",
        "preco_venda": Decimal("1.30"),
        "validade_horas": 24,
        "conservacao": "ambiente",
        "rendimento_lote": 100,
    }
    base.update(alteracoes)
    return base


def test_cria_produto_valido():
    produto = Produto(**dados(nome="  Pastel   de nata "))
    assert produto.nome == "Pastel de nata"
    assert produto.preco_venda == Decimal("1.30")
    assert produto.ativo is True
    assert produto.id is None


@pytest.mark.parametrize("campo, valor", [
    ("nome", 123),
    ("preco_venda", 1.30),
    ("validade_horas", True),
    ("ativo", 1),
])
def test_tipo_errado_da_type_error(campo, valor):
    with pytest.raises(TypeError):
        Produto(**dados(**{campo: valor}))


@pytest.mark.parametrize("campo, valor", [
    ("nome", "   "),
    ("categoria", ""),
    ("preco_venda", Decimal("-0.01")),
    ("preco_venda", Decimal("1.234")),
    ("validade_horas", 0),
    ("rendimento_lote", 0),
    ("conservacao", "frio"),
])
def test_valor_invalido_da_value_error(campo, valor):
    with pytest.raises(DadosProdutoInvalidos):
        Produto(**dados(**{campo: valor}))


def test_desativar():
    produto = Produto(**dados())
    produto.desativar()
    assert produto.ativo is False
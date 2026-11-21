"""Testes da conversão dos campos dos formulários (web/formularios.py)."""

from decimal import Decimal

import pytest

from web.formularios import CampoInvalido, para_decimal, para_inteiro


@pytest.mark.parametrize("texto, esperado", [
    ("2,50", Decimal("2.50")),    # vírgula portuguesa
    ("2.50", Decimal("2.50")),    # ponto
    (" 903 ", Decimal("903")),    # espaços à volta
])
def test_para_decimal_aceita_numeros(texto, esperado):
    assert para_decimal(texto, "erro") == esperado


@pytest.mark.parametrize("texto", ["", None, "abc", "1,5,3"])
def test_para_decimal_recusa_texto(texto):
    with pytest.raises(CampoInvalido, match="O preço tem de ser um número."):
        para_decimal(texto, "O preço tem de ser um número.")


def test_para_inteiro_aceita_inteiro():
    assert para_inteiro(" 24 ", "erro") == 24


@pytest.mark.parametrize("texto", ["", None, "abc", "2,5"])
def test_para_inteiro_recusa_texto(texto):
    with pytest.raises(CampoInvalido, match="Escolha uma matéria-prima."):
        para_inteiro(texto, "Escolha uma matéria-prima.")
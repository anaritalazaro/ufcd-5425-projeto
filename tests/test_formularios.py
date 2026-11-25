"""Testes da conversão dos campos dos formulários (web/formularios.py)."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from web.formularios import (CampoInvalido, para_data, para_data_hora,
                             para_decimal, para_inteiro)


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


def test_para_data_hora_aceita_valor_do_navegador():
    esperado = datetime(2026, 11, 22, 9, 30)
    assert para_data_hora("2026-11-22T09:30", "erro") == esperado


@pytest.mark.parametrize("texto", ["", None, "22/11/2026 09:30",
                                   "2026-02-30T09:30"])
def test_para_data_hora_recusa_texto(texto):
    mensagem = "Indique a data e a hora de produção."
    with pytest.raises(CampoInvalido, match=mensagem):
        para_data_hora(texto, mensagem)


def test_para_data_aceita_valor_do_navegador():
    assert para_data("2026-11-23", "erro") == date(2026, 11, 23)


@pytest.mark.parametrize("texto", ["", None, "23/11/2026", "2026-02-30"])
def test_para_data_recusa_texto(texto):
    with pytest.raises(CampoInvalido, match="Indique uma data válida."):
        para_data(texto, "Indique uma data válida.")

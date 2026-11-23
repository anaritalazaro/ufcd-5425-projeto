"""Conversão dos campos dos formulários nos tipos do Python (camada web).

O navegador envia sempre texto. Estas funções só convertem o tipo; as
regras (maior do que zero, casas decimais, máximo) ficam no domínio.
[Sebenta 5425, 10.1; revisão do PR #27, ponto 7]
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation


class CampoInvalido(ValueError):
    """Um campo do formulário não tem o tipo esperado (ex.: "abc" no preço).

    Exceção da camada web: o domínio não sabe que os dados vêm de um
    formulário. É subclasse de ValueError, como as do domínio. [Prop]
    """


def para_decimal(texto: str | None, mensagem: str) -> Decimal:
    """Converte um número escrito com vírgula ou ponto num Decimal."""
    # texto or "": um campo em falta (None) passa a vazio e dá a mensagem.
    # strip() tira os espaços; a vírgula portuguesa passa a ponto.
    limpo = (texto or "").strip().replace(",", ".")
    try:
        return Decimal(limpo)
    except InvalidOperation:
        # from None: a mensagem do utilizador não leva o erro interno.
        raise CampoInvalido(mensagem) from None


def para_inteiro(texto: str | None, mensagem: str) -> int:
    """Converte um número inteiro escrito no formulário num int."""
    try:
        return int((texto or "").strip())
    except ValueError:
        raise CampoInvalido(mensagem) from None


def para_data_hora(texto: str | None, mensagem: str) -> datetime:
    """Converte o valor de um campo datetime-local num datetime."""
    # O navegador envia sempre AAAA-MM-DDTHH:MM, seja qual for o formato
    # que mostra ao utilizador. [Mozilla Developer Network (MDN),
    # input type="datetime-local"]
    try:
        return datetime.strptime((texto or "").strip(), "%Y-%m-%dT%H:%M")
    except ValueError:
        raise CampoInvalido(mensagem) from None


def para_data(texto: str | None, mensagem: str) -> date:
    """Converte o valor de um campo date (AAAA-MM-DD) num date."""
    # Como no datetime-local, o navegador envia sempre este formato.
    # [MDN, input type="date"]
    try:
        return datetime.strptime((texto or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        raise CampoInvalido(mensagem) from None

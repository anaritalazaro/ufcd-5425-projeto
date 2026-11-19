"""Validações partilhadas pelas classes do domínio."""

from decimal import Decimal

def decimal_validado(valor, campo: str, casas: int, maximo: Decimal,
                     excecao: type[ValueError], *, positivo: bool = False) -> Decimal:
    
    """Valida um Decimal não negativo (ou positivo) com um número máximo de casas.
    Os limites vêm do tipo DECIMAL da coluna no schema.sql."""
    
    if type(valor) is not Decimal:
        raise TypeError(f"O campo {campo} tem de ser Decimal.")
    if not valor.is_finite():
        raise excecao(f"O campo {campo} tem de ser um número.")
    if positivo and valor <= 0:
        raise excecao(f"O campo {campo} tem de ser maior do que zero.")
    if valor < 0:
        raise excecao(f"O campo {campo} não pode ser negativo.")
    if valor >= maximo:
        raise excecao(f"O campo {campo} é demasiado alto.")
    
    menor_unidade = Decimal(1).scaleb(-casas)  # 3 casas -> 0.001; 6 casas -> 0.000001

    if valor != valor.quantize(menor_unidade):
        raise excecao(f"O campo {campo} tem no máximo {casas} casas decimais.")
    return valor.quantize(menor_unidade)
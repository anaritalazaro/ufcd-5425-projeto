from decimal import Decimal

CONSERVACOES = ("ambiente", "refrigerado", "congelado")
PRECO_MAXIMO = Decimal("100000000")  # DECIMAL(10,2): até 99 999 999,99
CENTIMO = Decimal("0.01")


class DadosProdutoInvalidos(ValueError):
    """Um dado do produto tem um valor inválido."""


def _texto(valor, campo: str, maximo: int) -> str:
    if type(valor) is not str:
        raise TypeError(f"O campo {campo} tem de ser texto.")
    texto = " ".join(valor.split())
    if not texto:
        raise DadosProdutoInvalidos(f"O campo {campo} é obrigatório.")
    if len(texto) > maximo:
        raise DadosProdutoInvalidos(f"O campo {campo} não pode exceder {maximo} caracteres.")
    return texto


def _inteiro_positivo(valor, campo: str) -> int:
    if type(valor) is not int:
        raise TypeError(f"O campo {campo} tem de ser um número inteiro.")
    if valor <= 0:
        raise DadosProdutoInvalidos(f"O campo {campo} tem de ser maior do que zero.")
    return valor


class Produto:
    def __init__(self, *, nome, categoria, preco_venda, validade_horas,
                 conservacao, rendimento_lote, ativo=True, id=None):
        self.id = id
        self.nome = nome
        self.categoria = categoria
        self.preco_venda = preco_venda
        self.validade_horas = validade_horas
        self.conservacao = conservacao
        self.rendimento_lote = rendimento_lote
        self.ativo = ativo

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor) -> None:
        self._nome = _texto(valor, "nome", 120)

    @property
    def categoria(self) -> str:
        return self._categoria

    @categoria.setter
    def categoria(self, valor) -> None:
        self._categoria = _texto(valor, "categoria", 60)

    @property
    def preco_venda(self) -> Decimal:
        return self._preco_venda

    @preco_venda.setter
    def preco_venda(self, valor) -> None:
        if type(valor) is not Decimal:
            raise TypeError("O preço de venda tem de ser Decimal.")
        if not valor.is_finite():
            raise DadosProdutoInvalidos("O preço de venda tem de ser um número.")
        if valor < 0:
            raise DadosProdutoInvalidos("O preço de venda não pode ser negativo.")
        if valor >= PRECO_MAXIMO:
            raise DadosProdutoInvalidos("O preço de venda é demasiado alto.")
        if valor != valor.quantize(CENTIMO):
            raise DadosProdutoInvalidos("O preço de venda tem no máximo duas casas decimais.")
        self._preco_venda = valor.quantize(CENTIMO)

    @property
    def validade_horas(self) -> int:
        return self._validade_horas

    @validade_horas.setter
    def validade_horas(self, valor) -> None:
        self._validade_horas = _inteiro_positivo(valor, "validade_horas")

    @property
    def conservacao(self) -> str:
        return self._conservacao

    @conservacao.setter
    def conservacao(self, valor) -> None:
        if type(valor) is not str:
            raise TypeError("A conservação tem de ser texto.")
        if valor not in CONSERVACOES:
            raise DadosProdutoInvalidos(
                f"A conservação tem de ser uma de: {', '.join(CONSERVACOES)}."
            )
        self._conservacao = valor

    @property
    def rendimento_lote(self) -> int:
        return self._rendimento_lote

    @rendimento_lote.setter
    def rendimento_lote(self, valor) -> None:
        self._rendimento_lote = _inteiro_positivo(valor, "rendimento_lote")

    @property
    def ativo(self) -> bool:
        return self._ativo

    @ativo.setter
    def ativo(self, valor) -> None:
        if type(valor) is not bool:
            raise TypeError("O campo ativo tem de ser verdadeiro ou falso.")
        self._ativo = valor

    def desativar(self) -> None:
        """RN11: um produto nunca se apaga; deixa de estar ativo."""
        self._ativo = False

    def __str__(self) -> str:
        return f"{self.nome} ({self.categoria}, {self.preco_venda} €)"
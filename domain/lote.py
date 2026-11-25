"""Lote de produção (RF04): código, validade e estado (RN06, RN08, RN12, RN13)."""

from datetime import datetime, timedelta
from decimal import Decimal

TURNOS = ("manhã", "tarde")                     # [DD] RN12, ck_lote_turno
ESTADOS = ("aberto", "fechado", "rejeitado")    # [DD] RN13, ck_lote_estado


class DadosLoteInvalidos(ValueError):
    """Um dado do lote tem um valor inválido."""


class LoteJaRegistado(DadosLoteInvalidos):
    """Já existe um lote com este código (RN06, UNIQUE da coluna lote)."""

    def __init__(self, codigo_lote: str):
        # O código vai até ao minuto, como o campo datetime-local (J-06):
        # dois lotes do mesmo produto no mesmo minuto têm o mesmo código.
        super().__init__(
            "Já existe um lote deste produto registado neste minuto "
            f"(código {codigo_lote}). Se não for repetido, registe-o no "
            "minuto seguinte.")


class FechoInvalido(DadosLoteInvalidos):
    """RF07: um ou mais lotes do dia têm quantidades inválidas; nada foi
    gravado."""

    def __init__(self, erros: dict[int, str]):
        # id do lote -> mensagem, para a página assinalar cada lote
        # (ficha do RF07, Sprint 2, 6.3) [Prop].
        self.erros = erros
        super().__init__(
            "O dia não foi fechado. Corrija os lotes assinalados.")


class StockInsuficiente(DadosLoteInvalidos):
    """RF04: falta stock de uma ou mais matérias-primas; nada foi gravado."""

    def __init__(self, faltas: list[tuple[str, Decimal, str]]):
        # Guarda todas as faltas, para a página as mostrar (ficha do RF04, Sprint 2) [Prop].
        self.faltas = faltas
        detalhe = "; ".join(f"{nome}: faltam {quantidade} {unidade}"
                            for nome, quantidade, unidade in faltas)
        super().__init__(f"Stock insuficiente. {detalhe}.")


def _data_hora(valor, campo: str) -> datetime:
    if type(valor) is not datetime:
        raise TypeError(f"O campo {campo} tem de ser datetime.")
    return valor


def _inteiro(valor, campo: str, *, minimo: int, opcional: bool = False) -> int | None:
    # type() e não isinstance(): True e False não passam por inteiros (como no Produto).
    if valor is None and opcional:
        return None
    if type(valor) is not int:
        raise TypeError(f"O campo {campo} tem de ser um número inteiro.")
    if valor < minimo:
        raise DadosLoteInvalidos(f"O campo {campo} tem de ser maior ou igual a {minimo}.")
    return valor


class Lote:
    """Lote de produção. O __init__ reconstrói um lote lido da base de dados;
    um lote novo cria-se com Lote.novo()."""

    def __init__(self, *, id_produto, codigo_lote, data_hora_producao, turno, qtd_produzida,
                 validade, qtd_planeada=None, qtd_vendida=None, qtd_desperdicada=None,
                 estado="aberto", id=None):
        if type(id_produto) is not int or id_produto <= 0:
            raise TypeError("O lote precisa do id de um produto gravado.")
        if type(codigo_lote) is not str:
            raise TypeError("O código do lote tem de ser texto.")
        if not codigo_lote.strip() or len(codigo_lote) > 40:      # VARCHAR(40) NOT NULL
            raise DadosLoteInvalidos("O código do lote é obrigatório e tem no máximo 40 caracteres.")
        if turno not in TURNOS:
            raise DadosLoteInvalidos(f"O turno tem de ser um de: {', '.join(TURNOS)}.")
        if estado not in ESTADOS:
            raise DadosLoteInvalidos(f"O estado tem de ser um de: {', '.join(ESTADOS)}.")

        data_hora_producao = _data_hora(data_hora_producao, "data_hora_producao")
        validade = _data_hora(validade, "validade")
        if validade <= data_hora_producao:              # ck_lote_validade
            raise DadosLoteInvalidos("A validade tem de ser posterior à produção.")

        qtd_produzida = _inteiro(qtd_produzida, "qtd_produzida", minimo=1)
        qtd_planeada = _inteiro(qtd_planeada, "qtd_planeada", minimo=0, opcional=True)
        qtd_vendida = _inteiro(qtd_vendida, "qtd_vendida", minimo=0, opcional=True)
        qtd_desperdicada = _inteiro(qtd_desperdicada, "qtd_desperdicada", minimo=0, opcional=True)

        # RN10, ck_lote_fecho: um lote fechado tem produzido = vendido + desperdiçado.
        if estado == "fechado" and (
            qtd_vendida is None or qtd_desperdicada is None
            or qtd_vendida + qtd_desperdicada != qtd_produzida
        ):
            raise DadosLoteInvalidos(
                "Num lote fechado, vendido + desperdiçado tem de ser igual ao produzido."
            )

        # O id fica como atributo simples: o repositório atribui-o depois do INSERT (como no Produto).
        self.id = id
        self._id_produto = id_produto
        self._codigo_lote = codigo_lote
        self._data_hora_producao = data_hora_producao
        self._turno = turno
        self._qtd_planeada = qtd_planeada
        self._qtd_produzida = qtd_produzida
        self._qtd_vendida = qtd_vendida
        self._qtd_desperdicada = qtd_desperdicada
        self._validade = validade
        self._estado = estado

    # Construtor alternativo (UFCD 10794): recebe o produto e trata do código e da validade.
    @classmethod
    def novo(cls, produto, *, qtd_produzida, turno, data_hora_producao,
             qtd_planeada=None) -> "Lote":
        """Cria um lote novo, aberto (RN13), para um produto ativo."""
        if produto.id is None:
            raise TypeError("O lote precisa de um produto gravado.")
        # Inativos ficam fora das escolhas novas (RN11; validado pelo formador no PR #24).
        if not produto.ativo:
            raise DadosLoteInvalidos(f"O produto «{produto.nome}» está inativo.")
        data_hora_producao = _data_hora(data_hora_producao, "data_hora_producao")
        return cls(
            id_produto=produto.id,
            codigo_lote=cls.gerar_codigo(produto.id, data_hora_producao),
            data_hora_producao=data_hora_producao,
            turno=turno,
            # A qtd_planeada fica para o plano do dia (RF08, fase 1): a ficha
            # do RF04 não a pede, por isso a página do lote não a envia.
            qtd_planeada=qtd_planeada,
            qtd_produzida=qtd_produzida,
            validade=cls.calcular_validade(data_hora_producao, produto.validade_horas),
        )

    # Cálculos sem estado (UFCD 10794): não usam o objeto e testam-se sozinhos.
    @staticmethod
    def calcular_validade(data_hora_producao: datetime, validade_horas: int) -> datetime:
        """RN08: validade = produção + validade do produto, em horas."""
        return data_hora_producao + timedelta(hours=validade_horas)

    @staticmethod
    def gerar_codigo(id_produto: int, data_hora_producao: datetime) -> str:
        """Código P007-20261120-0930: produto, data e hora ao minuto.

        Proposta adaptada da sugestão do formador no PR #17. Com o UNIQUE da coluna,
        registar o mesmo lote duas vezes no mesmo minuto é recusado (RN06).
        """
        return f"P{id_produto:03d}-{data_hora_producao:%Y%m%d-%H%M}"

    def fechar(self, qtd_vendida: int, qtd_desperdicada: int) -> None:
        """RF07, RN10: regista o vendido e o desperdiçado e fecha o lote."""
        # Só um lote aberto se fecha (RN13): não se fecha duas vezes.
        if self._estado != "aberto":
            raise DadosLoteInvalidos(
                f"O lote {self._codigo_lote} já está {self._estado}.")
        # type() e não isinstance(): True e False não passam por inteiros.
        if type(qtd_vendida) is not int or type(qtd_desperdicada) is not int:
            raise TypeError(
                "O vendido e o desperdiçado têm de ser inteiros.")
        if qtd_vendida < 0 or qtd_desperdicada < 0:
            raise DadosLoteInvalidos(
                "O vendido e o desperdiçado não podem ser negativos.")
        # RN10, ck_lote_fecho: produzido = vendido + desperdiçado.
        if qtd_vendida + qtd_desperdicada != self._qtd_produzida:
            raise DadosLoteInvalidos(
                "Vendido + desperdiçado tem de ser igual ao produzido "
                f"({self._qtd_produzida}).")
        self._qtd_vendida = qtd_vendida
        self._qtd_desperdicada = qtd_desperdicada
        self._estado = "fechado"

    # Só getters: só o fechar() altera o lote, e só uma vez (RF07, RN13).
    @property
    def id_produto(self) -> int: return self._id_produto
    @property
    def codigo_lote(self) -> str: return self._codigo_lote
    @property
    def data_hora_producao(self) -> datetime: return self._data_hora_producao
    @property
    def turno(self) -> str: return self._turno
    @property
    def qtd_planeada(self) -> int | None: return self._qtd_planeada
    @property
    def qtd_produzida(self) -> int: return self._qtd_produzida
    @property
    def qtd_vendida(self) -> int | None: return self._qtd_vendida
    @property
    def qtd_desperdicada(self) -> int | None: return self._qtd_desperdicada
    @property
    def validade(self) -> datetime: return self._validade
    @property
    def estado(self) -> str: return self._estado

    def __str__(self) -> str:
        return f"{self.codigo_lote} ({self.qtd_produzida} un., {self.estado})"
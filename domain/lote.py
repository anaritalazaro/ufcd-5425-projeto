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
        super().__init__(f"O lote {codigo_lote} já foi registado.")


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

    # Só getters: os dados do lote não se alteram depois de criados (o fecho, RF07, entra depois).
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
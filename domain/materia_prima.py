"""Matéria-prima e o seu stock (RF02)."""

from decimal import Decimal

from domain.movimento_stock import MAX_QUANTIDADE, MovimentoStock
from domain.validacao import decimal_validado

UNIDADES = ("g", "ml", "un")
MAX_CUSTO = Decimal("1000000")  # DECIMAL(12,6)


class DadosMateriaPrimaInvalidos(ValueError):
    """Um dado da matéria-prima tem um valor inválido."""


class NomeMateriaPrimaDuplicado(DadosMateriaPrimaInvalidos):
    """Já existe uma matéria-prima com este nome (RN01)."""

    def __init__(self, nome: str):
        super().__init__(f"Já existe uma matéria-prima com o nome «{nome}».")


class MateriaPrima:
    def __init__(self, *, nome, unidade, custo_unitario, stock_minimo=Decimal("0"),
                 stock_atual=Decimal("0"), alergenios=None, ativo=True, id=None):
        self.id = id
        self.nome = nome
        self.unidade = unidade
        self.custo_unitario = custo_unitario
        self.stock_minimo = stock_minimo
        self.alergenios = alergenios
        self.ativo = ativo
        # stock_atual não tem setter: só muda através de um movimento (D-02).
        self._stock_atual = decimal_validado(stock_atual, "stock_atual", 3,
                                             MAX_QUANTIDADE, DadosMateriaPrimaInvalidos)

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valor) -> None:
        if type(valor) is not str:
            raise TypeError("O campo nome tem de ser texto.")
        texto = " ".join(valor.split())
        if not texto:
            raise DadosMateriaPrimaInvalidos("O campo nome é obrigatório.")
        if len(texto) > 120:
            raise DadosMateriaPrimaInvalidos("O campo nome não pode exceder 120 caracteres.")
        self._nome = texto

    @property
    def unidade(self) -> str:
        return self._unidade

    @unidade.setter
    def unidade(self, valor) -> None:
        # RN02: uma só unidade-base, igual no stock e na receita; sem conversões.
        if type(valor) is not str:
            raise TypeError("A unidade tem de ser texto.")
        if valor not in UNIDADES:
            raise DadosMateriaPrimaInvalidos(f"A unidade tem de ser uma de: {', '.join(UNIDADES)}.")
        self._unidade = valor

    @property
    def custo_unitario(self) -> Decimal:
        return self._custo_unitario

    @custo_unitario.setter
    def custo_unitario(self, valor) -> None:
        # 6 casas: o custo é por g, ml ou un (sal a 0,000350 €/g) [Prop, validada no PR #17].
        self._custo_unitario = decimal_validado(valor, "custo_unitario", 6, MAX_CUSTO,
                                                DadosMateriaPrimaInvalidos)

    @property
    def stock_minimo(self) -> Decimal:
        return self._stock_minimo

    @stock_minimo.setter
    def stock_minimo(self, valor) -> None:
        self._stock_minimo = decimal_validado(valor, "stock_minimo", 3, MAX_QUANTIDADE,
                                              DadosMateriaPrimaInvalidos)

    @property
    def stock_atual(self) -> Decimal:
        return self._stock_atual

    @property
    def alergenios(self) -> str | None:
        return self._alergenios

    @alergenios.setter
    def alergenios(self, valor) -> None:
        # Campo opcional (TEXT sem NOT NULL): um texto vazio fica None.
        if valor is not None and type(valor) is not str:
            raise TypeError("Os alergénios têm de ser texto.")
        texto = " ".join(valor.split()) if valor else ""
        self._alergenios = texto or None

    @property
    def ativo(self) -> bool:
        return self._ativo

    @ativo.setter
    def ativo(self, valor) -> None:
        if type(valor) is not bool:
            raise TypeError("O campo ativo tem de ser verdadeiro ou falso.")
        self._ativo = valor

    def desativar(self) -> None:
        """RN11: nunca se apaga; deixa de estar ativa."""
        self._ativo = False

    def tem_stock(self, quantidade: Decimal) -> bool:
        """RN05: há stock suficiente para consumir esta quantidade? (usado no RF04)"""
        return self._stock_atual >= quantidade

    def abaixo_do_minimo(self) -> bool:
        """O stock atual está abaixo do stock mínimo?"""
        return self._stock_atual < self._stock_minimo

    def registar_entrada(self, quantidade: Decimal) -> MovimentoStock:
        """Cria o movimento de entrada e aplica-o ao stock. Devolve o movimento a gravar."""
        movimento = MovimentoStock(id_materia_prima=self.id, tipo="entrada", quantidade=quantidade)
        self._stock_atual = movimento.efeito_no_stock(self._stock_atual)
        return movimento

    def registar_consumo(self, quantidade: Decimal, id_lote: int) -> MovimentoStock:
        """RF04: cria o movimento de consumo do lote e desconta-o do stock.

        Faz o mesmo que o registar_entrada(), no sentido oposto [Prop]: a entrada soma, 
        o consumo subtrai e precisa do lote. O stock só muda através de um movimento (D-02).
        O serviço do lote já verificou todas as matérias-primas; o tem_stock() é a rede de
        segurança do domínio (RN05).
        """
        movimento = MovimentoStock(id_materia_prima=self.id, tipo="consumo",
                                   quantidade=quantidade, id_lote=id_lote)
        if not self.tem_stock(movimento.quantidade):
            raise DadosMateriaPrimaInvalidos(f"Stock insuficiente de «{self.nome}».")
        self._stock_atual = movimento.efeito_no_stock(self._stock_atual)
        return movimento

    def __str__(self) -> str:
        return f"{self.nome} ({self.stock_atual} {self.unidade})"
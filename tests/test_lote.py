from datetime import datetime
from decimal import Decimal

import pytest

from domain.lote import (DadosLoteInvalidos, FechoInvalido, Lote,
                          StockInsuficiente)
from domain.produto import Produto

PRODUCAO = datetime(2026, 11, 20, 9, 30)


def pastel(**alteracoes) -> Produto:
    base = {"nome": "Pastel de nata", "categoria": "Pastelaria", "preco_venda": Decimal("1.30"),
            "validade_horas": 24, "conservacao": "ambiente", "rendimento_lote": 100, "id": 7}
    base.update(alteracoes)
    return Produto(**base)


def dados(**alteracoes):
    """Dados de um lote lido da base de dados (__init__)."""
    base = {"id_produto": 7, "codigo_lote": "P007-20261120-0930", "data_hora_producao": PRODUCAO,
            "turno": "manhã", "qtd_produzida": 60, "validade": datetime(2026, 11, 21, 9, 30)}
    base.update(alteracoes)
    return base


def test_novo_calcula_codigo_validade_e_estado():
    lote = Lote.novo(pastel(), qtd_produzida=60, turno="manhã", data_hora_producao=PRODUCAO)
    assert lote.codigo_lote == "P007-20261120-0930"
    assert lote.validade == datetime(2026, 11, 21, 9, 30)    # RN08: + 24 horas
    assert lote.estado == "aberto"                            # RN13
    assert lote.id is None


def test_gerar_codigo_ignora_os_segundos():
    # No mesmo minuto, o código repete-se e o UNIQUE recusa o segundo registo (RN06).
    assert Lote.gerar_codigo(7, datetime(2026, 11, 20, 9, 30, 59)) == "P007-20261120-0930"


def test_calcular_validade_sem_objeto():
    assert Lote.calcular_validade(PRODUCAO, 4) == datetime(2026, 11, 20, 13, 30)


def test_novo_recusa_produto_inativo():
    with pytest.raises(DadosLoteInvalidos):
        Lote.novo(pastel(ativo=False), qtd_produzida=60, turno="manhã",
                  data_hora_producao=PRODUCAO)


@pytest.mark.parametrize("campo, valor", [
    ("turno", "noite"), ("estado", "perdido"), ("qtd_produzida", 0), ("qtd_planeada", -1),
    ("codigo_lote", " "), ("validade", PRODUCAO),
])
def test_valor_invalido_da_value_error(campo, valor):
    with pytest.raises(DadosLoteInvalidos):
        Lote(**dados(**{campo: valor}))


@pytest.mark.parametrize("campo, valor", [
    ("qtd_produzida", True), ("qtd_produzida", "60"), ("data_hora_producao", "2026-11-20"),
])
def test_tipo_errado_da_type_error(campo, valor):
    with pytest.raises(TypeError):
        Lote(**dados(**{campo: valor}))


@pytest.mark.parametrize("vendida, desperdicada", [(None, 10), (50, 5)])
def test_lote_fechado_exige_produzido_igual_a_vendido_mais_desperdicado(vendida, desperdicada):
    with pytest.raises(DadosLoteInvalidos):
        Lote(**dados(estado="fechado", qtd_vendida=vendida, qtd_desperdicada=desperdicada))


def test_atributos_so_de_leitura():
    lote = Lote(**dados())
    with pytest.raises(AttributeError):
        lote.codigo_lote = "P007-20261120-1000"


def test_stock_insuficiente_indica_todas_as_faltas():
    erro = StockInsuficiente([("Farinha T65", Decimal("1234.000"), "g"),
                              ("Ovos", Decimal("3.000"), "un")])
    assert len(erro.faltas) == 2
    assert "Farinha T65" in str(erro) and "Ovos" in str(erro)


def test_fechar_regista_quantidades_e_estado():
    lote = Lote(**dados())
    lote.fechar(52, 8)                     # 52 + 8 = 60 produzidos (RN10)
    assert (lote.qtd_vendida, lote.qtd_desperdicada) == (52, 8)
    assert lote.estado == "fechado"


@pytest.mark.parametrize("vendida, desperdicada", [
    (50, 5),     # soma diferente do produzido (RN10)
    (70, -10),   # negativo, mesmo com a soma certa
])
def test_fechar_recusa_quantidades_invalidas(vendida, desperdicada):
    lote = Lote(**dados())
    with pytest.raises(DadosLoteInvalidos):
        lote.fechar(vendida, desperdicada)
    assert lote.estado == "aberto"         # nada mudou


def test_fechar_recusa_tipo_errado():
    with pytest.raises(TypeError):
        Lote(**dados()).fechar("52", 8)


def test_fechar_recusa_lote_ja_fechado():
    lote = Lote(**dados())
    lote.fechar(60, 0)
    with pytest.raises(DadosLoteInvalidos, match="já está fechado"):
        lote.fechar(60, 0)


def test_fecho_invalido_guarda_os_erros_por_lote():
    erro = FechoInvalido({3: "Vendido + desperdiçado tem de ser igual "
                             "ao produzido (60)."})
    assert 3 in erro.erros
    assert isinstance(erro, DadosLoteInvalidos)

from decimal import Decimal

import pytest

from domain.linha_receita import DadosReceitaInvalidos, LinhaReceita


def linha(quantidade="1505"):
    return LinhaReceita(id_produto=1, id_materia_prima=2,
                        quantidade_para_rendimento=Decimal(quantidade))


def test_consumo_proporcional_criterio_do_rf04():
    # 60 pastéis com 1 505 g de farinha para 100 consomem 903 g (Sprint 3, critério do RF04)
    assert linha().consumo_para(60, 100) == Decimal("903.000")


def test_consumo_arredonda_para_cima_a_3_casas():
    # 1 × 0,5 ÷ 3 = 0,1666... -> 0,167
    assert linha("0.5").consumo_para(1, 3) == Decimal("0.167")


def test_consumo_pequeno_nunca_fica_zero():
    assert linha("0.001").consumo_para(1, 100) == Decimal("0.001")


@pytest.mark.parametrize("quantidade", ["0", "-1", "1.2345"])
def test_quantidade_invalida(quantidade):
    with pytest.raises(DadosReceitaInvalidos):
        linha(quantidade)


def test_quantidade_tem_de_ser_decimal():
    with pytest.raises(TypeError):
        LinhaReceita(id_produto=1, id_materia_prima=2, quantidade_para_rendimento=1505)


@pytest.mark.parametrize("qtd, rendimento", [(0, 100), (60, 0)])
def test_consumo_com_valores_invalidos(qtd, rendimento):
    with pytest.raises(DadosReceitaInvalidos):
        linha().consumo_para(qtd, rendimento)


def test_consumo_recusa_bool():
    with pytest.raises(TypeError):
        linha().consumo_para(True, 100)
"""Dados de demonstração: matérias-primas, stock, produtos e receitas.

Usa os serviços da aplicação, por isso as validações são as mesmas das
páginas (decisoes.md, Receitas: as receitas não têm páginas nesta versão).
Os valores são aproximados, só para demonstrar o sistema.

Uso, com o contentor a correr e a base de dados criada pelo schema.sql:
    python dados_demonstracao.py

Pode correr mais do que uma vez: o que já existe (pelo nome) não se cria
nem recebe stock outra vez; as receitas são substituídas.
"""

from decimal import Decimal

from config import ConfiguracaoBD
from database import abrir_ligacao
from repositories.materia_prima_repository import MateriaPrimaRepository
from repositories.movimento_stock_repository import MovimentoStockRepository
from repositories.produto_repository import ProdutoRepository
from repositories.receita_repository import ReceitaRepository
from services.materia_prima_service import MateriaPrimaService
from services.produto_service import ProdutoService
from services.receita_service import ReceitaService

# (nome, unidade, custo por unidade em €, stock mínimo, alergénios,
#  entrada de stock inicial)
# Ovos em gramas, e não em unidades: o consumo proporcional (RN04) dá
# casas decimais, que só fazem sentido em peso.
MATERIAS_PRIMAS = [
    ("Farinha T55", "g", "0.000850", "5000", "glúten", "25000"),
    ("Açúcar", "g", "0.001100", "3000", None, "10000"),
    ("Leite gordo", "ml", "0.000900", "4000", "leite", "12000"),
    ("Gemas pasteurizadas", "g", "0.008000", "1000", "ovos", "3000"),
    ("Ovo inteiro pasteurizado", "g", "0.005000", "1000", "ovos", "4000"),
    ("Manteiga", "g", "0.009000", "2000", "leite", "5000"),
    ("Fermento de padeiro", "g", "0.006000", "200", None, "1000"),
    # Abaixo do mínimo de propósito: mostra o aviso na lista do stock.
    ("Canela em pó", "g", "0.030000", "50", None, "30"),
    # Unidade "un": só para o que se usa sempre inteiro.
    ("Caixas de 6", "un", "0.150000", "50", None, "200"),
]

# (nome, categoria, preço de venda em €, validade em horas, conservação,
#  rendimento do lote)
PRODUTOS = [
    ("Pastel de nata", "Pastelaria", "1.20", 24, "ambiente", 60),
    ("Bola de Berlim", "Pastelaria", "1.50", 24, "refrigerado", 40),
    ("Queque de canela", "Bolos", "1.00", 48, "ambiente", 20),
]

# Produto -> {matéria-prima: quantidade para o rendimento do lote}.
RECEITAS = {
    "Pastel de nata": {
        "Farinha T55": "900", "Açúcar": "640", "Leite gordo": "1070",
        "Gemas pasteurizadas": "240", "Manteiga": "450",
        "Canela em pó": "5",
    },
    "Bola de Berlim": {
        "Farinha T55": "1500", "Açúcar": "300", "Leite gordo": "600",
        "Ovo inteiro pasteurizado": "300", "Gemas pasteurizadas": "120",
        "Manteiga": "200", "Fermento de padeiro": "45",
    },
    "Queque de canela": {
        "Farinha T55": "500", "Açúcar": "400",
        "Ovo inteiro pasteurizado": "400", "Manteiga": "300",
        "Leite gordo": "100", "Canela em pó": "10",
    },
}


def criar_materias_primas(servico: MateriaPrimaService) -> dict[str, int]:
    """Cria as matérias-primas que faltam, com a entrada de stock inicial."""
    existentes = {m.nome: m.id for m in servico.listar_materias_primas()}
    for nome, unidade, custo, minimo, alergenios, entrada in MATERIAS_PRIMAS:
        if nome in existentes:
            print(f"Já existe: {nome}")
            continue
        materia = servico.criar_materia_prima(
            nome=nome, unidade=unidade, custo_unitario=Decimal(custo),
            stock_minimo=Decimal(minimo), alergenios=alergenios)
        # O stock inicial entra como movimento, como na página (D-02).
        servico.registar_entrada(materia.id, Decimal(entrada))
        existentes[nome] = materia.id
        print(f"Criada: {nome} ({entrada} {unidade})")
    return existentes


def criar_produtos(servico: ProdutoService) -> dict[str, int]:
    """Cria os produtos que faltam."""
    existentes = {p.nome: p.id for p in servico.listar_produtos()}
    for nome, categoria, preco, validade, conservacao, rendimento in PRODUTOS:
        if nome in existentes:
            print(f"Já existe: {nome}")
            continue
        produto = servico.criar_produto(
            nome=nome, categoria=categoria, preco_venda=Decimal(preco),
            validade_horas=validade, conservacao=conservacao,
            rendimento_lote=rendimento)
        existentes[nome] = produto.id
        print(f"Criado: {nome}")
    return existentes


def criar_receitas(servico: ReceitaService, produtos: dict[str, int],
                   materias: dict[str, int]) -> None:
    """Grava (ou substitui) a receita de cada produto."""
    for nome_produto, linhas in RECEITAS.items():
        quantidades = {materias[nome]: Decimal(qtd)
                       for nome, qtd in linhas.items()}
        servico.guardar_receita(produtos[nome_produto], quantidades)
        print(f"Receita: {nome_produto} ({len(quantidades)} linhas)")


def main() -> None:
    conn = abrir_ligacao(ConfiguracaoBD.do_ambiente())
    try:
        materias_repo = MateriaPrimaRepository(conn)
        produtos_repo = ProdutoRepository(conn)
        materias = criar_materias_primas(MateriaPrimaService(
            conn, materias_repo, MovimentoStockRepository(conn)))
        produtos = criar_produtos(ProdutoService(conn, produtos_repo))
        criar_receitas(ReceitaService(conn, ReceitaRepository(conn),
                                      produtos_repo, materias_repo),
                       produtos, materias)
    finally:
        conn.close()
    print("Dados de demonstração prontos.")


if __name__ == "__main__":
    main()
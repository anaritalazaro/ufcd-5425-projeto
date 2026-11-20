"""Rotas dos produtos: listar e criar (RF01). Sem SQL (RNF01)."""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from database import ErroLigacaoBD, abrir_ligacao
from domain.produto import CONSERVACOES, DadosProdutoInvalidos
from repositories.produto_repository import ProdutoRepository
from services.produto_service import ProdutoService

bp = Blueprint("produtos", __name__, url_prefix="/produtos")

MENSAGEM_SEM_BD = "Não foi possível ligar à base de dados. Tente mais tarde."


def construir_servico(conn) -> ProdutoService:
    """Constrói o serviço com o repositório, sobre a ligação do pedido [Sebenta 5425, 10.2]."""
    return ProdutoService(conn, ProdutoRepository(conn))


def converter_formulario(formulario) -> dict:
    """Converte o texto do formulário nos tipos que o Produto espera."""
    # A rota só converte os tipos; as regras ficam no Produto. [Sebenta 5425, 10.1]
    try:
        preco = Decimal(formulario.get("preco_venda", "").strip().replace(",", "."))
    except InvalidOperation:
        raise DadosProdutoInvalidos("O preço de venda tem de ser um número.") from None
    try:
        validade = int(formulario.get("validade_horas", ""))
        rendimento = int(formulario.get("rendimento_lote", ""))
    except ValueError:
        raise DadosProdutoInvalidos(
            "A validade e o rendimento do lote têm de ser números inteiros."
        ) from None
    return {
        "nome": formulario.get("nome", ""),
        "categoria": formulario.get("categoria", ""),
        "preco_venda": preco,
        "validade_horas": validade,
        "conservacao": formulario.get("conservacao", ""),
        "rendimento_lote": rendimento,
    }


@bp.route("/")
def lista():
    """GET /produtos: mostra todos os produtos."""
    try:
        conn = abrir_ligacao(current_app.config["BD"])
    except ErroLigacaoBD as erro:
        # Mensagem genérica na página; detalhe só no terminal (decisoes.md §9).
        current_app.logger.warning("Sem ligação ao PostgreSQL: %s", erro.__cause__)
        return render_template("produtos/lista.html", produtos=[], erro=MENSAGEM_SEM_BD), 503
    try:
        produtos = construir_servico(conn).listar_produtos()
    finally:
        conn.close()
    return render_template("produtos/lista.html", produtos=produtos, erro=None)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    """GET mostra o formulário vazio; POST valida e grava o produto."""
    if request.method == "GET":
        return render_template("produtos/formulario.html",
                               dados={}, erro=None, conservacoes=CONSERVACOES)

    dados = request.form.to_dict()
    try:
        valores = converter_formulario(dados)
        conn = abrir_ligacao(current_app.config["BD"])
        try:
            construir_servico(conn).criar_produto(**valores)
        finally:
            conn.close()
    except DadosProdutoInvalidos as erro:
        # Inclui o nome repetido (NomeProdutoDuplicado é subclasse).
        # Devolve o formulário com os dados escritos e a mensagem. [Prop: 422]
        return render_template("produtos/formulario.html", dados=dados,
                               erro=str(erro), conservacoes=CONSERVACOES), 422
    except ErroLigacaoBD as erro:
        current_app.logger.warning("Sem ligação ao PostgreSQL: %s", erro.__cause__)
        return render_template("produtos/formulario.html", dados=dados,
                               erro=MENSAGEM_SEM_BD, conservacoes=CONSERVACOES), 503
    # Redireciona depois de gravar: atualizar a página não volta a enviar o formulário.
    return redirect(url_for("produtos.lista"))
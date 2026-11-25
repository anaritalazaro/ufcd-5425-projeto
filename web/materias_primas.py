"""Rotas das matérias-primas: listar, criar e registar uma entrada de stock (RF02). Sem SQL (RNF01)."""

# A partir do Flask, uso dos equivalentes do FastAPI [sebenta 5425, seccao 10]
from flask import Blueprint, current_app, redirect, render_template, request, url_for

# Imports do que a rota usa das outras camadas
from database import ErroLigacaoBD, abrir_ligacao
from domain.materia_prima import UNIDADES, DadosMateriaPrimaInvalidos
from domain.movimento_stock import DadosMovimentoInvalidos
from repositories.materia_prima_repository import MateriaPrimaRepository
from repositories.movimento_stock_repository import MovimentoStockRepository
from services.materia_prima_service import MateriaPrimaService
from web.formularios import CampoInvalido, para_decimal, para_inteiro

# "materias_primas": nome interno, usado no url_for("materias_primas.lista").
# url_prefix: início comum dos endereços; @bp.route("/nova") passa a /materias-primas/nova.
# [Flask, Blueprints; na sebenta, o equivalente é o APIRouter, secção 10]
bp = Blueprint("materias_primas", __name__, url_prefix="/materias-primas")

MENSAGEM_SEM_BD = "Não foi possível ligar à base de dados. Tente mais tarde."


def construir_servico(conn) -> MateriaPrimaService:
    """Constrói o serviço com os dois repositórios, sobre a mesma ligação [Sebenta 5425, 10.2]."""
    # A mesma ligação nos dois repositórios põe o movimento e o stock na mesma transação (D-02)
    return MateriaPrimaService(conn, MateriaPrimaRepository(conn), MovimentoStockRepository(conn))


def sem_ligacao(erro, template: str, **contexto):
    """Mostra a mensagem genérica (503); o detalhe fica no terminal (decisoes.md, 9)."""
    # erro.__cause__ é a exceção original do psycopg, guardada pelo raise ... from erro do database.py.
    current_app.logger.warning("Sem ligação ao PostgreSQL: %s", erro.__cause__)

    # **contexto passa ao template os outros dados de que a página precisa.
    return render_template(template, erro=MENSAGEM_SEM_BD, **contexto), 503


@bp.route("/")
def lista():
    """GET /materias-primas: mostra as matérias-primas e o stock."""
    try:
        conn = abrir_ligacao(current_app.config["BD"])
    except ErroLigacaoBD as erro:
        return sem_ligacao(erro, "materias_primas/lista.html", materias=[])
    # Uma ligação por pedido, fechada no finally [Sebenta 5425, 10.2]
    try:
        materias = construir_servico(conn).listar_materias_primas()
    finally:
        conn.close()
    return render_template("materias_primas/lista.html", materias=materias, erro=None)


@bp.route("/nova", methods=["GET", "POST"])
def nova():
    """GET mostra o formulário vazio; POST valida e grava a matéria-prima."""
    # request.form.to_dict(): os campos enviados num dicionário (vazio no GET).
    # contexto junta o que o formulário precisa, para não o repetir em cada render_template.
    contexto = {"dados": request.form.to_dict(), "unidades": UNIDADES}
    if request.method == "GET":
        return render_template("materias_primas/formulario.html", erro=None, **contexto)
    dados = contexto["dados"]
    try:
        # A rota só converte os tipos; as regras ficam na MateriaPrima [Sebenta 5425, 10.1]
        valores = {
            "nome": dados.get("nome", ""),
            "unidade": dados.get("unidade", ""),
            "custo_unitario": para_decimal(
                dados.get("custo_unitario"),
                "O custo unitário tem de ser um número."),
            "stock_minimo": para_decimal(
                dados.get("stock_minimo") or "0",
                "O stock mínimo tem de ser um número."),
            "alergenios": dados.get("alergenios"),
        }
        conn = abrir_ligacao(current_app.config["BD"])
        try:
            construir_servico(conn).criar_materia_prima(**valores)
        finally:
            conn.close()
    except (DadosMateriaPrimaInvalidos, CampoInvalido) as erro:
        # DadosMateriaPrimaInvalidos inclui o nome repetido (NomeMateriaPrima-
        # Duplicado é subclasse); CampoInvalido vem da conversão.
        # Devolve o formulário com a mensagem e os dados escritos [Prop: 422].
        return render_template("materias_primas/formulario.html", erro=str(erro), **contexto), 422
    except ErroLigacaoBD as erro:
        return sem_ligacao(erro, "materias_primas/formulario.html", **contexto)
    return redirect(url_for("materias_primas.lista"))


@bp.route("/entrada", methods=["GET", "POST"])
def entrada():
    """GET mostra o formulário da entrada; POST regista a entrada de stock."""
    dados = request.form.to_dict()
    # Id escolhido, já como int, para o template marcar a opção (#41).
    id_escolhido = None
    # A ligação abre-se antes de distinguir GET e POST: os dois precisam da
    # lista para o menu
    try:
        conn = abrir_ligacao(current_app.config["BD"])
    except ErroLigacaoBD as erro:
        return sem_ligacao(erro, "materias_primas/entrada.html", materias=[], dados=dados)
    try:
        servico = construir_servico(conn)
        if request.method == "POST":
            try:
                id_escolhido = para_inteiro(
                    dados.get("id_materia_prima"),
                    "Escolha uma matéria-prima.")
                quantidade = para_decimal(
                    dados.get("quantidade"),
                    "A quantidade tem de ser um número.")
                servico.registar_entrada(id_escolhido, quantidade)
                return redirect(url_for("materias_primas.lista"))
            # Um except pode apanhar várias exceções, entre parênteses:
            # CampoInvalido (id ou quantidade que não são números), a da
            # matéria-prima (não existe) e a do movimento (quantidade 0,
            # casas a mais).
            except (DadosMateriaPrimaInvalidos, DadosMovimentoInvalidos,
                    CampoInvalido) as erro:
                # A transação falhada já foi desfeita; a mesma ligação volta a listar [psycopg 3, Transactions]
                return render_template("materias_primas/entrada.html",
                                       materias=servico.listar_materias_primas(),
                                       dados=dados, id_escolhido=id_escolhido,
                                       erro=str(erro)), 422
        return render_template("materias_primas/entrada.html",
                               materias=servico.listar_materias_primas(),
                               dados=dados, id_escolhido=id_escolhido,
                               erro=None)
    finally:
        # Fecha a ligação em qualquer caso: GET, POST com sucesso ou POST com erro
        conn.close()

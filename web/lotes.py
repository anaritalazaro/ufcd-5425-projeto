"""Rotas dos lotes de produção: registar um lote (RF04) e fechar o dia
(RF07, RF15). Sem SQL (RNF01)."""

from datetime import date, datetime

from flask import (Blueprint, current_app, redirect, render_template,
                   request, url_for)

from database import ErroLigacaoBD, abrir_ligacao
from domain.lote import (TURNOS, DadosLoteInvalidos, FechoInvalido,
                         StockInsuficiente)
from repositories.lote_repository import LoteRepository
from repositories.materia_prima_repository import MateriaPrimaRepository
from repositories.movimento_stock_repository import MovimentoStockRepository
from repositories.produto_repository import ProdutoRepository
from repositories.receita_repository import ReceitaRepository
from services.lote_service import LoteService
from services.produto_service import ProdutoService
from web.formularios import (CampoInvalido, para_data, para_data_hora,
                             para_inteiro)
# A mesma resposta 503 das matérias-primas, sem a repetir aqui.
from web.materias_primas import sem_ligacao

# "lotes": nome interno, usado no url_for("lotes.novo").
# [Flask, Blueprints; na sebenta, o equivalente é o APIRouter, secção 10]
bp = Blueprint("lotes", __name__, url_prefix="/lotes")

TEMPLATE = "lotes/formulario.html"
TEMPLATE_FECHO = "lotes/fecho.html"
MENSAGEM_QUANTIDADES = ("O vendido e o desperdiçado têm de ser números "
                        "inteiros.")

def construir_servicos(conn) -> tuple[LoteService, ProdutoService]:
    """Constrói os serviços do lote e dos produtos na mesma ligação."""
    # Todos os repositórios na mesma ligação: o lote, os consumos e o
    # stock ficam na mesma transação (D-02, RN06) [Sebenta 5425, 10.2].
    produtos = ProdutoRepository(conn)
    lotes = LoteService(conn, LoteRepository(conn), produtos,
                        ReceitaRepository(conn), MateriaPrimaRepository(conn),
                        MovimentoStockRepository(conn))
    # O serviço dos produtos só serve para o menu.
    return lotes, ProdutoService(conn, produtos)


@bp.route("/novo", methods=["GET", "POST"])
def novo():
    """GET mostra o formulário; POST regista o lote e dá saída do stock."""
    dados = request.form.to_dict()
    if request.method == "GET":
        # Sugere a data e a hora atuais: o lote regista-se no arranque da
        # produção, para o stock descer logo e mostrar o real.
        # Continua editável. Formato do datetime-local.
        # [MDN, input type="datetime-local"]
        dados["data_hora_producao"] = datetime.now().strftime(
            "%Y-%m-%dT%H:%M")
    # Id escolhido, já como int, para o template marcar a opção (como #41).
    id_escolhido = None
    # Matérias-primas em falta, para a página as mostrar numa lista.
    faltas = []
    try:
        conn = abrir_ligacao(current_app.config["BD"])
    except ErroLigacaoBD as erro:
        return sem_ligacao(erro, TEMPLATE, produtos=[], turnos=TURNOS,
                           dados=dados, id_escolhido=id_escolhido,
                           faltas=faltas)
    try:
        servico, servico_produtos = construir_servicos(conn)
        if request.method == "POST":
            try:
                # A rota só converte os tipos; as regras ficam no Lote e no
                # serviço [Sebenta 5425, 10.1; #42].
                id_escolhido = para_inteiro(
                    dados.get("id_produto"),
                    "Escolha um produto.")
                qtd_produzida = para_inteiro(
                    dados.get("qtd_produzida"),
                    "A quantidade produzida tem de ser um número inteiro.")
                data_hora = para_data_hora(
                    dados.get("data_hora_producao"),
                    "Indique a data e a hora de produção.")
                # O turno não se converte: o Lote recusa o que não estiver
                # em TURNOS (RN12).
                servico.registar_lote(id_escolhido, data_hora,
                                      dados.get("turno", ""), qtd_produzida)
                # Os lotes do dia mostram o lote novo, aberto (RF15).
                return redirect(url_for("lotes.fecho",
                                        dia=data_hora.date().isoformat()))
            # DadosLoteInvalidos inclui o StockInsuficiente e o
            # LoteJaRegistado (subclasses); CampoInvalido vem da conversão.
            except (DadosLoteInvalidos, CampoInvalido) as erro:
                if isinstance(erro, StockInsuficiente):
                    faltas = erro.faltas
                # A transação falhada já foi desfeita: a mesma ligação
                # volta a listar os produtos [psycopg 3, Transactions].
                return render_template(
                    TEMPLATE, produtos=servico_produtos.listar_produtos(),
                    turnos=TURNOS, dados=dados, id_escolhido=id_escolhido,
                    faltas=faltas, erro=str(erro)), 422
        return render_template(
            TEMPLATE, produtos=servico_produtos.listar_produtos(),
            turnos=TURNOS, dados=dados, id_escolhido=id_escolhido,
            faltas=faltas, erro=None)
    finally:
        # Fecha a ligação em qualquer caso (GET, POST com sucesso ou erro)
        conn.close()


@bp.route("/fecho", methods=["GET", "POST"])
def fecho():
    """GET mostra os lotes de um dia; POST fecha o dia (RF07, RN10)."""
    dados = request.form.to_dict()
    # O dia vem do endereço (?dia=2026-11-23) ou do formulário; sem dia,
    # é hoje. request.values junta os dois.
    texto_dia = request.values.get("dia") or date.today().isoformat()
    erro = None
    erros = {}            # id do lote → mensagem (ficha do RF07)
    try:
        dia = para_data(texto_dia, "Indique uma data válida.")
    except CampoInvalido as erro_data:
        dia, erro = date.today(), str(erro_data)
    contexto = {"dia": dia, "dados": dados, "erros": erros}
    try:
        conn = abrir_ligacao(current_app.config["BD"])
    except ErroLigacaoBD as erro_bd:
        return sem_ligacao(erro_bd, TEMPLATE_FECHO, lotes=[], nomes={},
                           **contexto)
    try:
        servico, servico_produtos = construir_servicos(conn)
        estado_http = 200
        if request.method == "POST" and erro is None:
            try:
                # A rota só converte; as regras ficam no Lote (RN10).
                quantidades = {}
                for lote in servico.listar_do_dia(dia):
                    if lote.estado != "aberto":
                        continue
                    try:
                        quantidades[lote.id] = (
                            para_inteiro(dados.get(f"vendido_{lote.id}"),
                                         MENSAGEM_QUANTIDADES),
                            para_inteiro(dados.get(f"desperdicado_{lote.id}"),
                                         MENSAGEM_QUANTIDADES))
                    except CampoInvalido as erro_campo:
                        erros[lote.id] = str(erro_campo)
                if erros:
                    raise FechoInvalido(erros)
                servico.fechar_dia(dia, quantidades)
                return redirect(url_for("lotes.fecho", dia=dia.isoformat()))
            except FechoInvalido as erro_fecho:
                # Um ou mais lotes assinalados; nada foi gravado.
                erros.update(erro_fecho.erros)
                erro, estado_http = str(erro_fecho), 422
            except DadosLoteInvalidos as erro_lote:
                # Por exemplo, nenhum lote aberto neste dia.
                erro, estado_http = str(erro_lote), 422
        # Nomes dos produtos para a tabela: id → nome.
        nomes = {produto.id: produto.nome
                 for produto in servico_produtos.listar_produtos()}
        return render_template(TEMPLATE_FECHO,
                               lotes=servico.listar_do_dia(dia), nomes=nomes,
                               erro=erro, **contexto), estado_http
    finally:
        conn.close()
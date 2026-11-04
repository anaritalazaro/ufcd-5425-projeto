from flask import Blueprint, current_app, render_template

from database import ErroLigacaoBD, abrir_ligacao
from repositories.sistema_repository import SistemaRepository
from services.sistema_service import SistemaService

bp = Blueprint("estado", __name__)


def construir_servico(conn) -> SistemaService:
    return SistemaService(SistemaRepository(conn))


@bp.route("/estado")
def estado():
    try:
        conn = abrir_ligacao(current_app.config["BD"])
    except ErroLigacaoBD as erro:
        current_app.logger.warning("Sem ligação ao PostgreSQL: %s", erro.__cause__)
        return render_template("estado.html", versao=None, erro=str(erro)), 503
    try:
        versao = construir_servico(conn).versao_bd()
    finally:
        conn.close()
    return render_template("estado.html", versao=versao, erro=None)

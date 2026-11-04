from flask import Flask

from config import ConfiguracaoBD
from web.estado import bp as estado_bp
from web.inicio import bp as inicio_bp


def create_app():
    app = Flask(__name__)
    app.config["BD"] = ConfiguracaoBD.do_ambiente()
    app.register_blueprint(inicio_bp)
    app.register_blueprint(estado_bp)
    return app

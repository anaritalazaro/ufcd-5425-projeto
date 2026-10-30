from flask import Flask

from web.inicio import bp as inicio_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(inicio_bp)
    return app
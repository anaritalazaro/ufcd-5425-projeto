import psycopg

from config import ConfiguracaoBD


def abrir_ligacao(config: ConfiguracaoBD) -> psycopg.Connection:
    """Abre uma ligação nova ao PostgreSQL. Quem a abre é responsável por a fechar."""
    return psycopg.connect(
        host=config.host,
        port=config.porta,
        dbname=config.base_dados,
        user=config.utilizador,
        password=config.palavra_passe,
        connect_timeout=5,    #faz a ligação desistir ao fim de 5 segundos se o contentor estiver parado, em vez de ficar à espera.
    )
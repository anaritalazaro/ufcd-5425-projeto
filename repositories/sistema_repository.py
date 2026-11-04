import psycopg

#recebe a ligação no construtor, não escolhe a base de dados e executa o SQL
class SistemaRepository:                        
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def versao(self) -> str:
        #O conn.execute() do psycopg 3 funciona como o do sqlite3 que a sebenta usa, e devolve um cursor. 
        # O fetchone() devolve um tuplo, e o [0] tira a primeira coluna.
        linha = self.conn.execute("SELECT version()").fetchone()
        return linha[0]

    
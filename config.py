import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

FICHEIRO_ENV = Path(__file__).parent / ".env"


def _ler(nome: str) -> str:
    valor = os.environ.get(nome)
    if not valor:
        raise RuntimeError(f"Falta a variável de ambiente {nome} (ver .env.example).")
    return valor


@dataclass(frozen=True)   #torna a configuração imutável depois de criada
class ConfiguracaoBD:
    host: str
    porta: int
    base_dados: str
    utilizador: str
    palavra_passe: str = field(repr=False)      #impede que a palavra-passe apareça quando se faz print da configuração ou quando ela surge numa mensagem de erro do Flask em modo debug

    @classmethod
    def do_ambiente(cls) -> "ConfiguracaoBD":
        load_dotenv(FICHEIRO_ENV)    #lê o .env e coloca as variáveis no ambiente do processo
        return cls(
            host=_ler("POSTGRES_HOST"),
            porta=int(_ler("POSTGRES_PORT")),
            base_dados=_ler("POSTGRES_DB"),
            utilizador=_ler("POSTGRES_USER"),
            palavra_passe=_ler("POSTGRES_PASSWORD"),
        )
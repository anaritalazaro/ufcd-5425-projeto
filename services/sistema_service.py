from repositories.sistema_repository import SistemaRepository

#serviço para que a rota nunca fale diretamente com o repositório
class SistemaService:
    def __init__(self, repository: SistemaRepository):
        self.repository = repository

    def versao_bd(self) -> str:
        return self.repository.versao()
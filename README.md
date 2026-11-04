# Projeto Final - UFCD 5425
 
Aplicação web em Python desenvolvida no âmbito da UFCD 5425 – Projeto de tecnologias e programação de sistemas de informação (Opção B – projeto livre).
 
## FORNADA · SOBRA ZERO
 
O Fornada · Sobra Zero é uma aplicação para planear e registar a produção diária de uma pastelaria com fabrico próprio. Numa pastelaria, a quantidade a produzir decide-se muitas vezes a olho: produzir a mais gera desperdício e produzir a menos faz perder vendas. A aplicação junta num só sítio o que se planeia, o que se produz, as matérias-primas gastas, as temperaturas das vitrines e câmaras e o que, ao fecho, se vendeu ou deitou fora.
 
## Funcionalidades previstas

**Núcleo (primeira versão):**
 
- Gestão de produtos, matérias-primas e receitas
- Entrada e ajuste de stock das matérias-primas
- Registo da produção de um lote, com consumo automático das matérias-primas
- Fecho do dia com as quantidades vendidas e desperdiçadas

**Fases seguintes, só depois de o núcleo estar a funcionar:**
 
1. Plano do dia e cálculo antecipado das necessidades
2. Registo das temperaturas dos equipamentos e sinalização das ocorrências
3. Segurança: validação completa, tratamento de erros e proteção dos formulários
4. Autenticação, acesso por várias pessoas e perfis de utilizador
5. Rejeição automática de lotes por temperatura
6. Melhorias visuais (CSS)

## Tecnologias
 
- Python e Flask
- PostgreSQL
- Docker
- pytest

## Executar

Requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/), Python 3 e Git. O pgAdmin 4 é opcional.

Nesta fase, o Docker corre só a base de dados (PostgreSQL 18); a aplicação Flask corre no computador.

**1. Obter o código e criar o `.env`**

```powershell
git clone https://github.com/anaritalazaro/ufcd-5425-projeto.git
cd ufcd-5425-projeto
Copy-Item .env.example .env
```

Preenche o `.env` com `POSTGRES_HOST=localhost`, `POSTGRES_PORT=5433` e um nome de base de dados, utilizador e palavra-passe à escolha (em minúsculas, sem espaços nem `$`). O `.env` não vai para o GitHub.

**2. Arrancar a base de dados**

Com o Docker Desktop aberto:

```powershell
docker compose up -d
docker compose ps
```

O contentor `fornada-db` deve aparecer com o estado **Up** e a porta `127.0.0.1:5433->5432/tcp`. Os dados mantêm-se entre arranques. No pgAdmin, liga-te a `localhost`, porta `5433`, com as credenciais do `.env`.

**3. Arrancar a aplicação**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app main run --debug
```

A aplicação fica em http://127.0.0.1:5000. A ligação à base de dados está em construção.

**Parar:** `docker compose stop`. Não uses `docker compose down -v`, que apaga a base de dados.

Problemas no arranque: ver [docs/resolucao-problemas.md](docs/resolucao-problemas.md). As decisões sobre a porta e a versão estão em [docs/decisoes.md](docs/decisoes.md).
 
## Estrutura dos ficheiros
 
- `README.md` — descrição do projeto e instruções de execução
- `LOG.md` — registo de progresso por sessão
- `docker-compose.yml` — base de dados PostgreSQL em Docker
- `.env.example` — modelo das variáveis de configuração, sem valores reais
- `docs/decisoes.md` — decisões de âmbito e decisões técnicas do projeto
- `docs/resolucao-problemas.md` — resolução de problemas no arranque
- `docs/modelo-er.png` — modelo E-R preliminar
- `config.py` — configuração lida do ambiente (.env)
- `database.py` — abertura da ligação ao PostgreSQL
- `main.py` — create_app(): cria a aplicação Flask
- `requirements.txt` — dependências Python
- `.env.example`  — modelo das variáveis de ambiente (sem valores reais)
- `domain/` — classes e regras do problema
- `repositories/` —  acesso aos dados (SQL parametrizado)
- `services/` — operações e transações
- `web/`  — rotas Flask (blueprints)
- `templates/` — páginas HTML (Jinja2)

## Autoria
 
- Formanda: Ana Silva
- UFCD 5425
- Formador: Rúben Ferreira
 
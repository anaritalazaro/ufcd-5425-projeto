# Registo de progresso
 
## Sessão 1 — 19 a 23 de outubro de 2026
 
- Escolha do tema e da Opção B (projeto livre)
- Criação do repositório no GitHub e partilha do link com o formador
- Entrega inicial submetida no Moodle a 23/10: identificação do sistema, contexto, fronteiras, modelo E-R preliminar e justificação do SGBD
- Nota: Sprint 1 foi submetido na UFCD 10790 a 21/10

## Sessão 2 — 26 de outubro de 2026
 
- README com a descrição do projeto
- Registo de progresso (este ficheiro)
- Modelo E-R preliminar adicionado ao repositório, em `docs/`
- Decisões de âmbito após o feedback do formador à entrega inicial, em `docs/decisoes.md`: prioridades da primeira versão, gestão de stock por movimentos, receitas por quantidade-base, fecho do dia e temperaturas

## Sessão 3 — 30 de outubro de 2026
- Issue #1 (parte 1): arranque da aplicação Flask, requirements.txt e .env.example
- Nota: Sprint 2 foi submetido na UFCD 10790 a 30/10

## Sessão 4 — 2 de novembro de 2026

- Correção da formatação das funcionalidades no README
- Justificação das dependências registada em `docs/decisoes.md` (secção 6)
- PR #2 em rascunho ligado à issue #1; tarefas concluídas assinaladas na checklist (4 de 8)
- Entregas da UFCD 10790 (Sprints 1 e 2) e entrega inicial da UFCD 5425 adicionadas em `docs/entregas/` (PR #3)
- Início da parte 2 da issue #1: Docker Desktop instalado e verificado (WSL 2, `docker run hello-world`)
- Conflito de porta com o PostgreSQL local (5432) resolvido: PostgreSQL 18 em Docker na porta 5433 (`docs/decisoes.md`, secção 7)


## Sessão 5 — 3 de novembro de 2026 (fora da aula)

- Criado o `.env` local a partir do `.env.example`, confirmado fora do Git (`git check-ignore -v .env`)
- `docker-compose.yml` com o PostgreSQL 18, publicado só em `127.0.0.1:5433`, com os dados no volume `dados_postgres`
- Ligação verificada com o `psql` dentro do contentor e com o pgAdmin em `localhost:5433`; sub-issue #5 fechada
- Secção "Executar" do README escrita e testada a partir de uma base de dados vazia; problemas no arranque em `docs/resolucao-problemas.md`
- Secção 7 de `docs/decisoes.md` completada (porta em `127.0.0.1`, volume e credenciais) e introdução atualizada
- Pendente: ligação da aplicação à base de dados (#6); a sub-issue #7 fica aberta até esse passo entrar no README

## Sessão 6 — 4 de novembro de 2026 (fora da aula)

- Licença alterada de MIT para "todos os direitos reservados"
- Sub-issue #4: config.py lê as variáveis POSTGRES_* do .env com o python-dotenv; database.py abre a ligação com o psycopg; pacotes domain/, repositories/ e services/ criados
- Integração do main no branch e resolução do conflito no README
- Sub-issue #6: página /estado verifica a ligação ao PostgreSQL (rota → serviço → repositório, como na sebenta); testada com o contentor a correr (200) e parado (503)
- Nota: Sprint 3 foi submetido na UFCD 10790 a 04/11 (por validar pelo formador)

## Sessão 7 — 5 de novembro de 2026 (fora da aula)

- Sub-issue #7: secção "Executar" do README atualizada (Python 3.14, `py -3.14`, `python -m pip`, verificação em `/estado`, `Ctrl+C` no "Parar")
- `.env.example` corrigido: a porta passou de 5432 para 5433, de acordo com o `decisoes.md`
- README testado num clone novo, numa pasta à parte, com um volume e credenciais novos: a página `/estado` respondeu "OK" (PostgreSQL 18.6). 
- O teste revelou que o README não explicava como preencher o `.env` e que, com o `.env` vazio, o contentor para sem aviso; README e `resolucao-problemas.md` corrigidos
- Notas no `decisoes.md` sobre a estrutura do código, o nome real do volume e a página `/estado`

## Sessão 8 — 6 de novembro de 2026

- Revisão do PR #2 pelo formador: aprovado, com sugestões não bloqueadoras
- `requirements.txt` com as versões fixadas (Flask 3.1.3, psycopg[binary] 3.3.6, python-dotenv 1.2.4), verificadas numa instalação nova com o Python 3.14.6
- `docs/decisoes.md`: secção 6 com a fixação das versões e nova secção 10 com a evolução futura (pool de ligações, ciclo de vida das ligações, JSON em `/estado`)
- `load_dotenv()` mantido dentro de `do_ambiente()`, seguindo a sebenta (secções 7.1 e 13)
- Sprint 3 da UFCD 10790 acrescentado a `docs/entregas/`

## Sessão 9 — 6 e 7 de novembro de 2026 (fora da aula)

- Sub-issue #13: restrições do `docs/schema.sql` completadas a partir do dicionário de dados (UFCD 10790, Sprint 3): CHECK de valores permitidos, quantidades e regras condicionais do `movimento_stock`, regra do fecho do dia, `nome` único no equipamento e `ON DELETE RESTRICT` nas chaves estrangeiras; origem de cada restrição indicada no ficheiro
- Corrigidos dois erros herdados do export do drawDB: UNIQUE isolado em `id_materia_prima` e `id_lote` (passa a UNIQUE composto) e `DEFAULT 0` nas quantidades do lote
- `custo_unitario` (DECIMAL(12,6)) e `conservacao` (VARCHAR(20), com lista fixa de valores) ajustados a valores reais, a pensar nos dados de demonstração
- Restrições testadas no PostgreSQL 18 com casos tirados dos critérios de aceitação do Sprint 3
- Decisões registadas em `docs/decisoes.md` (secção 11)


## Sessão 10 — 9 de novembro de 2026

- #14: `docs/schema.sql` montado em `/docker-entrypoint-initdb.d/01-schema.sql`, só de leitura (commit c39dc68)
- #15: teste de raiz com `docker compose down -v` (sem dados reais): oito `CREATE TABLE` nos *logs*, oito tabelas no `\dt` e no pgAdmin
- #16: secção 12 de `docs/decisoes.md`; README com a criação das tabelas no primeiro arranque e o que fazer quando o `schema.sql` muda; novo problema em `docs/resolucao-problemas.md`
- Sub-issues #14 a #16 fechadas; #12 com 4/4, a aguardar a integração do PR #17
- Docker Desktop: versão atual 4.97.0 (Docker Engine 29.9.2, Compose v5.6.1); a 4.98.0 está disponível e exige o WSL 3.0.3 ou posterior (instalado: 3.0.3.0). Não foi instalada durante a aula, porque pode pedir para reiniciar. Decidido atualizar fora da aula; a partir de 20/11, sem atualizações até à defesa (27/11)

## Sessão 11 — 9 de novembro de 2026 (fora da aula)

- Docker Desktop atualizado de 4.97.0 para 4.99.0: Engine e cliente de 29.9.2 para 29.9.3, Compose de v5.6.1 para v5.7.0
- A versão 4.98.0 prevista foi ultrapassada pela 4.99.0, lançada no próprio dia; instalada depois de rever as notas de lançamento, por incluir a correção de segurança do WSL 2 (da 4.98.0) e a correção da corrupção dos dados do Engine quando o Windows Update desliga o Docker Desktop
- Contentor parado com `docker compose stop` antes da atualização
- Depois da atualização, o `docker compose up -d` recriou o contentor `fornada-db`; os registos (`docker compose logs db`) confirmam que o volume foi mantido ("Skipping initialization")
- Verificação: 8 tabelas no pgAdmin e página `/estado` com "OK" (PostgreSQL 18.6)

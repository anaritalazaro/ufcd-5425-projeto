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

## Sessão 7 — 5 de novembro de 2026 (fora da aula)

- Sub-issue #7: secção "Executar" do README atualizada (Python 3.14, `py -3.14`, `python -m pip`, verificação em `/estado`, `Ctrl+C` no "Parar")
- `.env.example` corrigido: a porta passou de 5432 para 5433, de acordo com o `decisoes.md`
- README testado num clone novo, numa pasta à parte, com um volume e credenciais novos: a página `/estado` respondeu "OK" (PostgreSQL 18.6). 
- O teste revelou que o README não explicava como preencher o `.env` e que, com o `.env` vazio, o contentor para sem aviso; README e `resolucao-problemas.md` corrigidos
- Notas no `decisoes.md` sobre a estrutura do código, o nome real do volume e a página `/estado`

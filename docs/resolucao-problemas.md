# Resolução de problemas

## `failed to connect to the docker API ... dockerDesktopLinuxEngine`

O Docker Desktop não está a correr. Abre-o, espera pelo **Engine running** e repete o comando.

## `ports are not available ... Only one usage of each socket address`

A porta 5433 está ocupada. Para ver por quem:

```powershell
netstat -ano | Select-String ":5433"
```

- Com uma linha `LISTENING`: outro programa usa a porta. Muda o `POSTGRES_PORT` no `.env` (por exemplo, para 5434).
- Sem nenhuma linha `LISTENING`: a porta ficou presa à configuração anterior do contentor, depois de alterar as portas no `docker-compose.yml`. Recria-o com `docker compose down` e `docker compose up -d`.

## `password authentication failed` ou `role "..." does not exist`

A imagem do PostgreSQL só lê `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` no primeiro arranque. Alterá-los depois no `.env` não muda a base de dados existente. Repõe os valores do primeiro arranque ou, se puderes perder os dados, recria a base de dados:

```powershell
docker compose down -v
docker compose up -d
```

## O contentor não aparece no `docker compose ps`

O `docker compose up -d` indica "Started", mas o `docker compose ps` não mostra o `fornada-db`: o contentor arrancou e parou logo a seguir.

Vê a causa com `docker compose logs db`. Se aparecer "Database is uninitialized and superuser password is not specified", o `POSTGRES_PASSWORD` do `.env` está vazio. Preenche o `.env`, grava-o, confirma com `Get-Content .env` e volta a correr `docker compose up -d`.

Não uses `POSTGRES_HOST_AUTH_METHOD=trust`, que a mensagem sugere: permite ligações sem palavra-passe.

## Tabelas em falta depois do arranque

O `schema.sql` só corre com o volume vazio. Vê os *logs*:

```powershell
docker compose logs db
```

- Com uma linha `ERROR` a seguir a "running /docker-entrypoint-initdb.d/01-schema.sql": o script falhou a meio. Corrige-o e recria a base de dados com `docker compose down -v` e `docker compose up -d`.
- Com "Skipping initialization": o volume já existia, e o script não correu. Recria a base de dados da mesma forma, sabendo que se perdem os dados.

## O PNG exportado do diagrama E-R não mostra as relações

O botão **Download image** do diagrama E-R do pgAdmin exporta as tabelas, mas não as linhas das relações (ficam só os pontos junto às colunas). É um erro conhecido do pgAdmin.

Faz uma captura do diagrama: maximiza a janela, recolhe o Object Explorer, carrega em **Zoom to fit** e usa `Windows + Shift + S`. Recorta só a área do diagrama, sem a barra de cima, que mostra o nome da base de dados e do utilizador.
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
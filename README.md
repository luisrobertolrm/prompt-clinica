Usa o PostGres

$env:DATABASE_URL="postgresql+psycopg2://postgres:post123%40@localhost:5432/clinica"

```
alembic revision --autogenerate -m "alteracao tabela"
```


senha post123@
```
$env:DATABASE_URL='postgresql+psycopg2://postgres:post123%40@localhost:5432/clinica'
alembic upgrade head
```


#Rodar o sistema  *ver se o main esta correto ou dentro de src, não rodei agora para testar*
**Bug pequeno depois de informar o cpf só da um enter**
```
 uv run --env-file=".env" src/main.py
```


# **Conteudo do .env**
```
ANTHROPIC_API_KEY="ESSA É A ANTHROPIC_API_KEY"
OPENAI_API_KEY="SuaChave"
GOOGLE_API_KEY="ESSA É A GOOGLE_API_KEY"

POSTGRES_USER="postgres"
POSTGRES_PASSWORD="post123@"
POSTGRES_DB="clinica"
PGDATA=/var/lib/postgresql/data

DB_DNS='postgresql://postgres:post123%40@127.0.0.1:5432/clinica'
DATABASE_URL='postgresql+psycopg2://postgres:post123%40@127.0.0.1:5432/clinica'
```

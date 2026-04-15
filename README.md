# Prompt Clínica (Multi Med)

Um sistema completo de atendimento com IA para clínicas médicas. O projeto conta com um Frontend construído em Angular e um Backend Python integrado com LangGraph para a automação e orquestração dos fluxos de conversação.

## 📂 Estrutura do Projeto

O repositório está organizado em dois módulos principais:

- **`angular/multi-med/`**: Interface web moderna desenvolvida em Angular 17.
- **`python/`**: Backend com FastAPI, processamento de NLP usando LangChain/LangGraph, e persistência de dados utilizando PostgreSQL e Alembic.

---

## 🚀 Como iniciar o Backend (Python)

A aplicação utiliza o utilitário **`uv`** para o controle e instalação de dependências de forma otimizada. É necessário possuir o Python >= 3.13 instalado.

### 1. Configurando as Variáveis de Ambiente (`.env`)
Na raiz do diretório `python`, crie ou edite o arquivo `.env` para incluir suas credenciais de banco e de agentes de IA:

```env
ANTHROPIC_API_KEY="SUA_CHAVE_AQUI"
OPENAI_API_KEY="SUA_CHAVE_AQUI"
GOOGLE_API_KEY="SUA_CHAVE_AQUI"

POSTGRES_USER="postgres"
POSTGRES_PASSWORD="post123@"
POSTGRES_DB="clinica"
PGDATA=/var/lib/postgresql/data

DB_DNS="postgresql://postgres:post123%40@127.0.0.1:5432/clinica"
DATABASE_URL="postgresql+psycopg2://postgres:post123%40@127.0.0.1:5432/clinica"
```

### 2. Rodando as Migrations do Banco (Alembic)
Antes de testar qualquer funcionalidade, as tabelas devem estar criadas no PostgreSQL:

```bash
cd python

# Para gerar uma nova migração (quando alterar algo em `/models`):
uv run alembic revision --autogenerate -m "sua alteracao"

# Para aplicar as migrações mais recentes no banco:
uv run alembic upgrade head
```

### 3. Executando o Backend

Você pode subir a aplicação como uma **API da Web** (necessária para que o Angular se comunique) ou apenas rodar de forma terminal (CLI) para realizar testes interativos:

- **Modo Servidor (FastAPI):**
  ```bash
  cd python
  uv run fastapi dev src/web_api.py
  ```
  *(A API vai subir no endereço http://127.0.0.1:8000)*

- **Modo Terminal / Interativo:**
  ```bash
  cd python
  uv run --env-file=".env" python src/main.py
  ```

---

## 🎨 Como iniciar o Frontend (Angular)

O FrontEnd é onde você visualizará os painéis administrativos da clínica, agendas, médicos etc.

### 1. Instalar as dependências
Abra um novo terminal e vá para o diretório frontend:
```bash
cd angular/multi-med
npm install
```

### 2. Inicializar o servidor do sistema:
```bash
npm start
```
*(O sistema ficará acessível no seu navegador pelo http://localhost:4200)*

# Project Structure

## Root Directory

```
.
├── .env                    # Environment variables (DATABASE_URL)
├── .python-version         # Python version specification
├── pyproject.toml          # Project configuration and dependencies
├── alembic.ini            # Alembic migration configuration
├── db.py                  # Database engine and session management
├── repositories.py        # Data access layer
└── teste_db.py           # Database connection test script
```

## Source Code (`src/`)

Main application code organized by functionality:

```
src/
├── main.py               # Application entry point
├── atendimento.py        # Patient service logic
└── ia/                   # AI agent implementation
    ├── graph.py          # LangGraph workflow definitions
    ├── state.py          # Agent state models
    ├── tools.py          # LangChain tools for agent actions
    └── prompt.py         # System prompts and messages
```

### Key Modules

- `main.py`: Entry point with two-phase flow (patient registration → menu interaction)
- `ia/graph.py`: Defines two graphs - `configure_graph_cadastro()` for registration, `configure_graph_menu()` for menu operations
- `ia/tools.py`: LangChain tools wrapping database operations (TOOLS for registration, TOOLS_MENU for appointments)
- `ia/state.py`: Pydantic models for agent state (State, Cliente)

## Database Layer (`models/`)

SQLAlchemy ORM models following domain entities:

```
models/
├── base.py              # SQLAlchemy Base class
├── common.py            # Shared enums and constants
├── entities.py          # Domain models (Pessoa, Medico, Paciente, Consulta, etc.)
└── __init__.py
```

### Entity Relationships

- `Pessoa` (Person) - Base entity for both patients and doctors
- `Paciente` (Patient) - Links to Pessoa
- `Medico` (Doctor) - Links to Pessoa, has specialties and availability
- `Consulta` (Appointment) - Links patient, doctor, and specialty
- `TipoEspecialidade` (Specialty Type) - Medical specialties
- `Procedimento` (Procedure) - Medical procedures
- `DisponibilidadeMedico` (Doctor Availability) - Scheduling slots

## Database Migrations (`migrations/`)

Alembic migration management:

```
migrations/
├── env.py                    # Migration environment configuration
├── script.py.mako           # Migration template
└── versions/                # Migration version files
    └── 55977980300d_inicial.py
```

## Scripts (`scripts/`)

Utility scripts for database operations:

```
scripts/
├── check_db.py          # Database connection verification
└── seed_postgres.sql    # Database seeding script
```

## Documentation

- `README.md` - Root level (minimal, contains DB connection example)
- `src/README.md` - Detailed feature documentation in Portuguese
- `*.mermaid` files - Architecture and flow diagrams (classe.mermaid, fluxo.mermaid, etc.)

## Configuration Files

- `.kiro/` - Kiro AI assistant configuration and steering rules
- `.vscode/` - VS Code workspace settings
- `.venv/` - Python virtual environment (excluded from git)

## Architectural Patterns

### Two-Graph Agent System
1. Registration Graph (`configure_graph_cadastro`): Handles patient lookup/registration
2. Menu Graph (`configure_graph_menu`): Handles appointment operations

### State Management
- LangGraph with InMemorySaver for conversation checkpointing
- Thread-based conversation isolation (thread_id in RunnableConfig)
- State updates via `atualizar_state_paciente_node` after tool execution

### Database Access
- Context manager pattern (`get_session()`) for automatic commit/rollback
- Repository pattern in `repositories.py`
- SQLAlchemy ORM with relationship mapping

## Import Path Configuration

Project root is added to `sys.path` in `src/main.py` to enable importing `db.py` and `models/` from anywhere.

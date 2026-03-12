# Technology Stack

## Language & Runtime

- Python 3.13+
- Package manager: `uv` (modern Python package manager)

## Core Frameworks & Libraries

### AI/LLM Stack
- LangChain Core (1.2.9+) - LLM orchestration
- LangGraph (1.0.8+) - Agent workflow graphs
- LangChain Google GenAI (4.2.0+) - Google AI integration
- LangChain OpenAI/Ollama - Multiple LLM provider support
- LangGraph Checkpoint Postgres (3.0.4+) - Conversation state persistence

### Database
- PostgreSQL with psycopg2/psycopg3
- SQLAlchemy (2.0.46+) - ORM
- Alembic (1.18.4+) - Database migrations

### Utilities
- Rich (14.3.2+) - Terminal UI and formatting
- py-linq (1.4.0+) - LINQ-style queries
- Pyppeteer (0.0.25+) - Browser automation

## Database Configuration

Connection string format:
```
postgresql+psycopg2://user:password@host:5432/database_name
```

Set via `DATABASE_URL` environment variable.

## Code Quality Tools

### Ruff (Linter & Formatter)
- Line length: 88 characters
- Target: Python 3.13
- Auto-fix enabled
- Format: double quotes, spaces (4-width), LF line endings
- Extensive rule set with specific ignores (print statements allowed, no docstring requirements)

### Pyright (Type Checker)
- Mode: standard
- Includes: src, tests, models
- Virtual environment: .venv

### Pytest
- Test path: tests/
- Python path: src/
- Color output enabled

## Common Commands

### Environment Setup
```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Check database connection
python scripts/check_db.py
```

### Code Quality
```bash
# Run linter
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .

# Type checking
pyright
```

### Running the Application
```bash
# Main application
python src/main.py

# Database test
python teste_db.py
```

## Build System

- Build backend: setuptools
- Package directory: src/
- Package name: prompt-clinica

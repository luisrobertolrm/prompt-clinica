from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Usa DATABASE_URL do ambiente. Exemplo:
# postgres+psycopg2://usuario:senha@host:5432/banco
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/gerador_fluxo_caixa"
)

# Loga os SQL emitidos pelo engine em stdout
# sql_logger = logging.getLogger("sqlalchemy.engine")
# if not sql_logger.handlers:
#     handler = logging.StreamHandler()
#     handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
#     sql_logger.addHandler(handler)
# sql_logger.setLevel(logging.INFO)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, future=True
)


@contextmanager
def get_session() -> Iterator[Session]:
    """Cria um escopo de sessao com commit/rollback automatico."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

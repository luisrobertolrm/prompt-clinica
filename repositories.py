from __future__ import annotations

import logging
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.engine import ScalarResult
from sqlalchemy.orm import Session

T = TypeVar("T")

# Dedicated logger for database operations only
logger = logging.getLogger("db.operations")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class Repository(Generic[T]):
    """Repositorio generico simples para CRUD basico."""

    def __init__(self, session: Session, model: type[T]) -> None:
        self.session = session
        self.model = model

    def add(self, obj: T) -> T:
        logger.info("add %s", self.model.__name__)
        self.session.add(obj)
        self.session.flush()  # garante PK gerada
        self.session.refresh(obj)  # sincroniza campos gerados
        return obj

    def get(self, obj_id: int) -> T | None:
        logger.info("get %s id=%s", self.model.__name__, obj_id)
        return self.session.get(self.model, obj_id)

    def list(self) -> ScalarResult[T]:
        logger.info("list %s", self.model.__name__)
        return self.session.scalars(select(self.model))

    def select(self, *criteria) -> ScalarResult[T]:
        """Executa um select com filtros arbitrarios do SQLAlchemy."""
        logger.info("select %s criteria=%s", self.model.__name__, criteria)
        stmt = select(self.model).where(*criteria)
        return self.session.scalars(stmt)

    def update(self, obj_id: int, data: dict) -> T | None:
        logger.info(
            "update %s id=%s data_keys=%s",
            self.model.__name__,
            obj_id,
            list(data.keys()),
        )
        obj = self.get(obj_id)
        if not obj:
            logger.warning("update %s id=%s not found", self.model.__name__, obj_id)
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        logger.info("delete %s id=%s", self.model.__name__, obj_id)
        obj = self.get(obj_id)
        if not obj:
            logger.warning("delete %s id=%s not found", self.model.__name__, obj_id)
            return False
        self.session.delete(obj)
        self.session.flush()
        return True

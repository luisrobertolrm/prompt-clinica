from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class Repository(Generic[T]):
    """Repositorio generico simples para CRUD basico."""

    def __init__(self, session: Session, model: type[T]) -> None:
        self.session = session
        self.model = model

    def add(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()  # garante PK gerada
        self.session.refresh(obj)  # sincroniza campos gerados
        return obj

    def get(self, obj_id: int) -> T | None:
        return self.session.get(self.model, obj_id)

    def list(self) -> Iterable[T]:
        return self.session.scalars(select(self.model))

    def update(self, obj_id: int, data: dict) -> T | None:
        obj = self.get(obj_id)
        if not obj:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        obj = self.get(obj_id)
        if not obj:
            return False
        self.session.delete(obj)
        self.session.flush()
        return True

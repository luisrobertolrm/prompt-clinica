from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    """Declarative base class for all ORM models."""


__all__ = ["Base"]

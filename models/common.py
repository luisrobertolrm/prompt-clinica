# logging.basicConfig(level=logging.INFO)
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from enum import IntEnum, StrEnum


class StatusDisponibilidadeMedico(IntEnum):
    LIVRE = 0
    OCUPADO = 1
    BLOQUEADO = 2


class StatusAprovacao(StrEnum):
    PENDENTE = "pendente"
    REJEITADO = "rejeitado"
    APROVADO = "aprovado"


__all__ = ["StatusAprovacao", "StatusDisponibilidadeMedico"]

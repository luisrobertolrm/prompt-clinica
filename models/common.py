from enum import Enum, StrEnum


class StatusDisponibilidadeMedico(Enum):
    LIVRE = 0
    OCUPADO = 1
    BLOQUEADO = 2


class StatusAprovacao(StrEnum):
    PENDENTE = "pendente"
    REJEITADO = "rejeitado"
    APROVADO = "aprovado"


__all__ = ["StatusAprovacao", "StatusDisponibilidadeMedico"]

from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator


class AgendaProcedimento(BaseModel):
    id_agenda: int
    data: datetime
    id_especialidade: int
    id_procedimento: int | None


class EspecialidadeProcedimento(BaseModel):
    id_especialidade_procedimento: int
    nome: str
    tipo: int


class DisponibilidadeAgenda(BaseModel):
    id_medico: int
    id_especialidade_procedimento: int
    tipo: int
    data: datetime


class Cliente(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str = Field(..., min_length=3)
    sexo: str | None = None
    email: str | None = None
    data_nascimento: str | None = None
    id_usuario: int | None = None

    @field_validator("cpf")
    @classmethod
    def cpf_deve_ser_numerico(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("cpf deve conter apenas dígitos")
        if len(value) != 11:
            raise ValueError("cpf deve ter 11 dígitos")
        return value

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("nome deve ter ao menos 3 caracteres")
        return value

    # @field_validator("rg")
    # @classmethod
    # def rg_nao_vazio(cls, value: str) -> str:
    #     value = value.strip()
    #     if len(value) < 5:
    #         raise ValueError("rg deve ter ao menos 5 caracteres")
    #     return value

    def as_dict(self) -> dict[str, str | int | None]:
        return self.model_dump()


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    paciente: NotRequired[Cliente | None]

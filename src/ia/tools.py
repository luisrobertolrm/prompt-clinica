from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, time

from langchain.tools import BaseTool, tool
from psycopg import Date
from pydantic import BaseModel, Field, field_validator


class Pessoa(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str = Field(..., min_length=3)
    rg: str = Field(..., min_length=5)
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

    @field_validator("rg")
    @classmethod
    def rg_nao_vazio(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 5:
            raise ValueError("rg deve ter ao menos 5 caracteres")
        return value

    def as_dict(self) -> dict[str, str | int | None]:
        return self.model_dump()


class AgendaProcedimento(BaseModel):
    id_agenda: int
    data: datetime
    id_especialidade: int
    id_procedimento: int


class EspecialidadeProcedimento(BaseModel):
    id_especialidade: int
    nome: str


@tool
def marcar_consulta_procedimento(
    dia: datetime | Date,
    id_especialidade: int,
    id_procedimento: int,
) -> AgendaProcedimento:
    """
    Marca um procedimento para o paciente.

    Args:
        dia: data/hora desejada (datetime ou Date).
        id_usuario: identificador do paciente.
        id_especialidade: identificador da especialidade médica.
        id_procedimento: identificador do procedimento.
    Return:
        AgendaProcedimento com dados simulados da agenda.
    """
    data_agendada = (
        dia
        if isinstance(dia, datetime)
        else datetime.combine(dia, time(hour=9, minute=0))
    )

    return AgendaProcedimento(
        id_agenda=1000,
        data=data_agendada,
        id_especialidade=id_especialidade,
        id_procedimento=id_procedimento,
    )


@tool
def desmarcar_consulta_procedimento(dia: datetime, id_agenda: int) -> bool:
    """
    Desmarca um procedimento previamente agendado.

    Args:
        dia: data/hora da agenda a desmarcar.
        id_agenda: identificador da agenda.
    Return:
        True quando a operação é simulada com sucesso.
    """
    return True


@tool
def confirmar_consulta_procedimento(id_agenda: int):
    """Confirma uma agenda pelo id."""
    return True


@tool
def consular_consulta_procedimento(
    id_usuario: int,
    dia: datetime | None,
    id_especialidade: int | None,
    id_procedimento: int | None,
) -> Sequence[AgendaProcedimento]:
    """
    Consulta agendas disponíveis para o usuário.

    Args:
        dia: data base para busca.
        id_usuario: identificador do paciente.
        id_especialidade: identificador da especialidade.
        id_procedimento: identificador do procedimento.
    Return:
        Lista simulada de AgendaProcedimento.
    """
    base = (
        datetime.combine(dia.date(), time(hour=9, minute=0))
        if isinstance(dia, datetime)
        else datetime.combine(datetime.now().date(), time(hour=9, minute=0))
    )

    especialidade = id_especialidade if id_especialidade is not None else 0
    procedimento = id_procedimento if id_procedimento is not None else 0
    return [
        AgendaProcedimento(
            id_agenda=1,
            data=base,
            id_especialidade=especialidade,
            id_procedimento=procedimento,
        ),
        AgendaProcedimento(
            id_agenda=2,
            data=base.replace(hour=10),
            id_especialidade=especialidade,
            id_procedimento=procedimento,
        ),
    ]


@tool
def cadastrar_alterar_cliente(
    cpf: str, nome: str, sexo: str
) -> dict[str, str | int | None] | None:
    """Cadastra ou altera um cliente e retorna seus dados."""
    return Pessoa(cpf=cpf, nome="Joao da Silva", rg="MG1234567", id_usuario=1).as_dict()


@tool
def consultar_cliente(cpf: str) -> dict[str, str | int | None] | None:
    """
    Procura uma pessoa pelo CPF e retorna seus dados.

    Args:
        cpf: CPF do cliente.
    Return:
        dict com dados da pessoa quando encontrado, ou None se não encontrado.
    """
    if cpf == "12345678900":
        return Pessoa(
            cpf=cpf, nome="Joao da Silva", rg="MG1234567", id_usuario=1
        ).as_dict()

    if cpf == "98765432100":
        return Pessoa(
            cpf=cpf, nome="Maria Souza", rg="SP9876543", id_usuario=2
        ).as_dict()

    return None


@tool
def consultar_especialidade_procedimento(especialidade: str):
    """
    Lista especialidades/procedimentos disponíveis.

    Args:
        especialidade: texto para filtragem (não aplicado nesta simulação).
    Return:
        Lista simulada de EspecialidadeProcedimento.
    """
    return [
        EspecialidadeProcedimento(id_especialidade=10, nome="Cardiologia"),
        EspecialidadeProcedimento(id_especialidade=20, nome="Ortopedia"),
        EspecialidadeProcedimento(id_especialidade=30, nome="Dermatologia"),
    ]


TOOLS: Sequence[BaseTool] = [
    marcar_consulta_procedimento,
    desmarcar_consulta_procedimento,
    confirmar_consulta_procedimento,
    consular_consulta_procedimento,
    cadastrar_alterar_cliente,
    consultar_cliente,
    consultar_especialidade_procedimento,
]

TOOLS_BY_NAME: dict[str, BaseTool] = {tool_obj.name: tool_obj for tool_obj in TOOLS}

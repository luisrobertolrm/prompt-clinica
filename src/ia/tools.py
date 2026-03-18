from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import date, datetime, time, timedelta
from typing import Any

from langchain.tools import BaseTool, tool
from rich import print
from sqlalchemy import select
from sqlalchemy.engine.url import make_url

from db import get_session
from ia.rag.especialidade_rag import buscar_especialidades_similares
from ia.rag.procedimento_rag import buscar_procedimentos_similares
from ia.state import (
    AgendaConsulta,
    AgendaProcedimento,
    AgendaViewModel,
    Cliente,
    DisponibilidadeAgenda,
    EspecialidadeProcedimento,
)
from models import (
    Consulta,
    DisponibilidadeMedico,
    Medico,
    MedicoEspecialidade,
    MedicoProcedimento,
    Paciente,
    Pessoa,
    Procedimento,
    TipoEspecialidade,
    TipoProcedimento,
)
from models.common import StatusDisponibilidadeMedico
from repositories import Repository

raw_url = os.getenv("DATABASE_URL", "")
if raw_url:
    masked_url = make_url(raw_url).set(password="***")
    print("DATABASE_URL:", masked_url)


def _buscar_slots_disponibilidade(
    id_especialidade_procedimento: int, tipo: int
) -> list[DisponibilidadeAgenda]:
    """Busca slots disponíveis nas próximas duas semanas em blocos de 20 minutos.

    Args:
        id_especialidade_procedimento: identificador da especialidade (tipo=1) ou procedimento (tipo=2).
        tipo: 1 para especialidade, 2 para procedimento.
    """
    hoje = datetime.now().date()
    limite = hoje + timedelta(days=14)
    duracao_minutos = 20
    slots: list[DisponibilidadeAgenda] = []

    with get_session() as session:
        medicos_stmt = select(Medico.id)

        if tipo == 1:
            medicos_stmt = medicos_stmt.where(
                Medico.especialidades.any(
                    MedicoEspecialidade.id_tipo_especialidade
                    == id_especialidade_procedimento
                )
            )
        else:
            medicos_stmt = medicos_stmt.where(
                Medico.medico_procedimentos.any(
                    MedicoProcedimento.id_tipo_procedimento
                    == id_especialidade_procedimento
                )
            )

        medicos_ids = list(session.scalars(medicos_stmt))
        if not medicos_ids:
            return []

        disponibilidades_stmt = select(DisponibilidadeMedico).where(
            DisponibilidadeMedico.id_medico.in_(medicos_ids),
            DisponibilidadeMedico.status == StatusDisponibilidadeMedico.LIVRE.value,
            DisponibilidadeMedico.data_inicio <= hoje,
            (
                (DisponibilidadeMedico.data_fim >= hoje)
                | (DisponibilidadeMedico.data_fim.is_(None))
            ),
        )

        disponibilidades = list(session.scalars(disponibilidades_stmt))

        for disp in disponibilidades:
            inicio = max(disp.data_inicio, hoje)
            fim = min(disp.data_fim, limite)

            dia_atual = inicio
            while dia_atual <= fim:
                if dia_atual.weekday() == disp.dia_semana:
                    inicio_dia = datetime.combine(dia_atual, disp.hora_inicio)
                    fim_dia = datetime.combine(dia_atual, disp.hora_fim)

                    horario_atual = inicio_dia
                    while horario_atual + timedelta(minutes=duracao_minutos) <= fim_dia:
                        slots.append(
                            DisponibilidadeAgenda(
                                id_medico=disp.id_medico,
                                id_especialidade_procedimento=id_especialidade_procedimento,
                                tipo=tipo,
                                data=horario_atual,
                                nome_medico=disp.medico.pessoa.nome,
                            )
                        )
                        horario_atual += timedelta(minutes=duracao_minutos)

                dia_atual += timedelta(days=1)

    slots.sort(key=lambda item: (item.data, item.id_medico))
    return slots


def _agrupar_slots(slots: list[DisponibilidadeAgenda]) -> list[AgendaViewModel]:
    """Agrupa slots por médico, organizando horários por data."""
    grupos: dict[int, AgendaViewModel] = {}
    for s in slots:
        if s.id_medico not in grupos:
            grupos[s.id_medico] = AgendaViewModel(
                id_medico=s.id_medico,
                nome_medico=s.nome_medico or "",
                id_tipo_especialidade=s.id_especialidade_procedimento,
                agenda_disponivel={},
            )
        dia = s.data.strftime("%Y-%m-%d")
        hora = s.data.strftime("%H:%M")
        grupos[s.id_medico]["agenda_disponivel"].setdefault(dia, []).append(hora)

    retorno = list(grupos.values())
    
    return retorno


@tool
def consultar_agenda_disponibilidade_consulta(id_especialidade: int) -> list[AgendaViewModel]:
    """Lista slots disponíveis para consulta nas próximas duas semanas.

    Args:
        id_especialidade: identificador da especialidade médica.
    Return:
        Lista de AgendaViewModel com médico e horários agrupados por data.
    """
    print("chamou consultar_agenda_disponibilidade_consulta")
    slots = _buscar_slots_disponibilidade(id_especialidade, tipo=1)
    return _agrupar_slots(slots)


@tool
def consultar_agenda_disponibilidade_procedimento(id_procedimento: int) -> list[AgendaViewModel]:
    """Lista slots disponíveis para procedimento nas próximas duas semanas.

    Args:
        id_procedimento: identificador do tipo de procedimento.
    Return:
        Lista de AgendaViewModel com médico e horários agrupados por data.
    """
    print("chamou consultar_agenda_disponibilidade_procedimento")
    slots = _buscar_slots_disponibilidade(id_procedimento, tipo=2)
    return _agrupar_slots(slots)


@tool
def marcar_consulta_procedimento(
    id_paciente: int,
    id_medico: int,
    dia: datetime,
    id_especialidade_procedimento: int,
    tipo: int,
) -> AgendaConsulta | AgendaProcedimento:
    """
    Marca uma consulta (tipo=1) ou procedimento (tipo=2) para o paciente.

    Args:
        id_paciente: identificador do paciente.
        id_medico: identificador do médico.
        dia: data/hora desejada.
        id_especialidade_procedimento: identificador da especialidade (tipo=1) ou procedimento (tipo=2).
        tipo: 1 para consulta, 2 para procedimento.
    Return:
        AgendaConsulta ou AgendaProcedimento com dados da agenda criada.
    """
    print("Parametros:")
    print(f"{id_paciente=}")
    print(f"{id_medico=}")
    print(f"{dia=}")
    print(f"{id_especialidade_procedimento=}")
    print(f"{tipo=}")

    if tipo == 1:
        with get_session() as session:
            repo = Repository(session, Consulta)
            consulta = Consulta(
                id_funcionario=1,
                id_medico=id_medico,
                id_paciente=id_paciente,
                id_tipo_especialidade=id_especialidade_procedimento,
                data_consulta=dia,
                data_criacao=datetime.now(),
                observacao=None,
            )
            repo.add(consulta)
            return AgendaConsulta(
                id_consulta=consulta.id,
                data=dia,
                id_especialidade=id_especialidade_procedimento,
            )
    else:
        return AgendaProcedimento(
            id_procedimento=1,
            data=dia,
            id_tipo_procedimento=id_especialidade_procedimento,
        )


@tool
def desmarcar_consulta(id_consulta: int) -> bool:
    """
    Desmarca uma consulta previamente agendada.
    Antes de chamar esta tool, use consultar_consulta para obter o id_consulta
    filtrando por especialidade ou dia.

    Args:
        id_consulta: identificador da consulta a desmarcar.
    Return:
        True quando a operação é realizada com sucesso.
    """
    return True


@tool
def desmarcar_procedimento(id_procedimento: int) -> bool:
    """
    Desmarca um procedimento previamente agendado.
    Antes de chamar esta tool, use consultar_procedimento para obter o id_procedimento
    filtrando por procedimento ou dia.

    Args:
        id_procedimento: identificador do procedimento a desmarcar.
    Return:
        True quando a operação é realizada com sucesso.
    """
    return True


@tool
def confirmar_consulta(id_consulta: int) -> bool:
    """
    Confirma uma consulta agendada pelo id.

    Args:
        id_consulta: identificador da consulta.
    Return:
        True para implementação posterior.
    """
    return True


@tool
def confirmar_procedimento(id_procedimento: int) -> bool:
    """
    Confirma um procedimento agendado pelo id.

    Args:
        id_procedimento: identificador do procedimento.
    Return:
        True para implementação posterior.
    """
    return True


@tool
def consultar_consulta(
    id_usuario: int,
    dia: datetime | None,
    id_especialidade: int | None,
) -> Sequence[AgendaConsulta]:
    """
    Consulta agendas de consulta do usuário.

    Args:
        id_usuario: identificador do paciente.
        dia: data base para busca.
        id_especialidade: identificador da especialidade.
    Return:
        Lista de AgendaConsulta.
    """
    base = (
        datetime.combine(dia.date(), time(hour=9, minute=0))
        if isinstance(dia, datetime)
        else datetime.combine(datetime.now().date(), time(hour=9, minute=0))
    )

    especialidade = id_especialidade if id_especialidade is not None else 0
    return [
        AgendaConsulta(id_consulta=1, data=base, id_especialidade=especialidade),
        AgendaConsulta(id_consulta=2, data=base.replace(hour=10), id_especialidade=especialidade),
    ]


@tool
def consultar_procedimento(
    id_usuario: int,
    dia: datetime | None,
    id_procedimento: int | None,
) -> Sequence[AgendaProcedimento]:
    """
    Consulta agendas de procedimento do usuário.

    Args:
        id_usuario: identificador do paciente.
        dia: data base para busca.
        id_procedimento: identificador do procedimento.
    Return:
        Lista de AgendaProcedimento.
    """
    base = (
        datetime.combine(dia.date(), time(hour=9, minute=0))
        if isinstance(dia, datetime)
        else datetime.combine(datetime.now().date(), time(hour=9, minute=0))
    )

    proc = id_procedimento if id_procedimento is not None else 0
    return [
        AgendaProcedimento(id_procedimento=1, data=base, id_tipo_procedimento=proc),
        AgendaProcedimento(id_procedimento=2, data=base.replace(hour=10), id_tipo_procedimento=proc),
    ]


@tool
def cadastrar_alterar_cliente(
    cpf: str,
    nome: str,
    sexo: str,
    email: str,
    data_nascimento: str,
) -> dict[str, str | int | None] | None:
    """Cadastra ou altera um paciente e retorna seus dados.

    Args:
        cpf: CPF com 11 dígitos numéricos.
        nome: nome completo (mínimo 3 caracteres).
        sexo: 'M' ou 'F'.
        email: e-mail válido.
        data_nascimento: data no formato DD/MM/AAAA.
    Return:
        dict com dados do paciente cadastrado, ou None em caso de erro.
    """
    cpf_digits: str = "".join(ch for ch in cpf if ch.isdigit())
    if len(cpf_digits) != 11:
        print(f"CPF inválido: {cpf}")
        return None

    if len(nome.strip()) < 3:
        print(f"Nome inválido: {nome}")
        return None

    if sexo not in ("M", "F"):
        print(f"Sexo inválido: {sexo}")
        return None

    if not email or "@" not in email:
        print(f"Email inválido: {email}")
        return None

    try:
        data_nasc: date = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
    except ValueError:
        print(f"Data de nascimento inválida: {data_nascimento}")
        return None

    with get_session() as session:
        repo_paciente: Repository[Paciente] = Repository(session, Paciente)
        existente = repo_paciente.select(
            Paciente.pessoa.has(Pessoa.cpf == cpf_digits)
        ).first()

        if existente is not None:
            existente.pessoa.nome = nome.strip()
            existente.pessoa.sexo = sexo
            existente.pessoa.email = email
            existente.pessoa.data_nascimento = data_nasc
            paciente = existente
        else:
            pessoa = Pessoa(
                nome=nome.strip(),
                cpf=cpf_digits,
                sexo=sexo,
                email=email,
                data_nascimento=data_nasc,
            )
            session.add(pessoa)
            session.flush()
            paciente = Paciente(id_pessoa=pessoa.id, ativo=True, pessoa=pessoa)
            session.flush()

        return Cliente(
            cpf=paciente.pessoa.cpf,
            nome=paciente.pessoa.nome,
            sexo=paciente.pessoa.sexo,
            email=paciente.pessoa.email,
            data_nascimento=paciente.pessoa.data_nascimento.strftime("%d/%m/%Y")
            if paciente.pessoa.data_nascimento
            else None,
            id_usuario=paciente.id_pessoa,
        ).as_dict()


@tool
def consultar_cliente(cpf: str) -> dict[str, str | int | None] | None:
    """
    consultar_cliente
    Consulta o Cliente pelo CPF e retorna seus dados.
    Args:
        cpf: CPF do cliente.
    Return:
        dict com dados da Cliente quando encontrado, ou None se não encontrado.
        nome not null
        data_nascimento not null
        sexo not null
        cpf not null
        email not null
        rg null
    """
    cpf_digits = "".join(ch for ch in cpf if ch.isdigit())
    if len(cpf_digits) != 11:
        print(f"cpf inválido para busca: {cpf}")
        return None

    with get_session() as session:
        repo_paciente = Repository(session, Paciente)

        result = repo_paciente.select(Paciente.pessoa.has(Pessoa.cpf == cpf_digits))

        paciente = result.first()  # primeiro registro ou None

        if paciente is not None:
            return Cliente(
                cpf=paciente.pessoa.cpf,
                nome=paciente.pessoa.nome,
                sexo=paciente.pessoa.sexo,
                email=paciente.pessoa.email,
                data_nascimento=paciente.pessoa.data_nascimento.strftime("%d/%m/%Y")
                if paciente.pessoa.data_nascimento
                else None,
                id_usuario=paciente.id_pessoa,
            ).as_dict()

    return None


# @tool
# def atualizar_state_paciente(
#     id: int,
#     cpf: str,
#     nome: str,
#     sexo: str,
#     email: str,
#     data_nascimento: datetime,
#     runtime: Annotated[ToolRuntime[State], InjectedToolArg],
# ) -> None:
#     """atualizar_state_paciente
#     Preenche o estado compartilhado do fluxo com dados do paciente (cpf, nome, sexo, email e data_nascimento)."""
#     runtime.state["paciente"] = Cliente(
#         cpf=cpf,
#         nome=nome,
#         sexo=sexo,
#         email=email,
#         data_nascimento=data_nascimento,
#         id_usuario=id,
#     )
#     print("passou aqui")


@tool
def consultar_especialidade(especialidade: str):
    """
    Lista especialidades disponíveis por similaridade semântica.

    Args:
        especialidade: texto para busca.
    Return:
        Lista de EspecialidadeProcedimento com tipo=1.
    """
    resultados = buscar_especialidades_similares(especialidade)
    return [
        EspecialidadeProcedimento(
            id_especialidade_procedimento=esp.id,
            nome=esp.descricao,
            tipo=1,
        )
        for esp in resultados
    ]


@tool
def consultar_procedimento_tipo(procedimento: str):
    """
    Lista procedimentos disponíveis por similaridade semântica.

    Args:
        procedimento: texto para busca.
    Return:
        Lista de EspecialidadeProcedimento com tipo=2.
    """
    resultados = buscar_procedimentos_similares(procedimento)
    return [
        EspecialidadeProcedimento(
            id_especialidade_procedimento=proc.id,
            nome=proc.descricao,
            tipo=2,
        )
        for proc in resultados
    ]


TOOLS: Sequence[BaseTool] = [
    cadastrar_alterar_cliente,
    consultar_cliente,
]

# Opção 1 - Marcar Consulta
TOOLS_MARCAR_CONSULTA: Sequence[BaseTool] = [
    consultar_especialidade,
    consultar_agenda_disponibilidade_consulta,
    marcar_consulta_procedimento,
]

# Opção 2 - Marcar Procedimento
TOOLS_MARCAR_PROCEDIMENTO: Sequence[BaseTool] = [
    consultar_procedimento_tipo,
    consultar_agenda_disponibilidade_procedimento,
    marcar_consulta_procedimento,
]

# Opção 3 - Consultar Agenda
TOOLS_CONSULTAR_AGENDA: Sequence[BaseTool] = [
    consultar_consulta,
    consultar_procedimento,
]

# Opção 4 - Desmarcar Consulta
TOOLS_DESMARCAR_CONSULTA: Sequence[BaseTool] = [
    consultar_consulta,
    desmarcar_consulta,
]

# Opção 4b - Desmarcar Procedimento
TOOLS_DESMARCAR_PROCEDIMENTO: Sequence[BaseTool] = [
    consultar_procedimento,
    desmarcar_procedimento,
]

# Opção 5 - Confirmar Consulta
TOOLS_CONFIRMAR_CONSULTA: Sequence[BaseTool] = [
    consultar_consulta,
    confirmar_consulta,
]

# Opção 5b - Confirmar Procedimento
TOOLS_CONFIRMAR_PROCEDIMENTO: Sequence[BaseTool] = [
    consultar_procedimento,
    confirmar_procedimento,
]

# Opção 6 - Consultar Especialidades Disponíveis
TOOLS_CONSULTAR_ESPECIALIDADES: Sequence[BaseTool] = [
    consultar_especialidade,
    consultar_procedimento_tipo,
]

# Todos os tools do menu (fallback)
TOOLS_MENU: Sequence[BaseTool] = [
    marcar_consulta_procedimento,
    desmarcar_consulta,
    desmarcar_procedimento,
    confirmar_consulta,
    confirmar_procedimento,
    consultar_consulta,
    consultar_procedimento,
    consultar_especialidade,
    consultar_procedimento_tipo,
    consultar_agenda_disponibilidade_consulta,
    consultar_agenda_disponibilidade_procedimento,
]

TOOLS_BY_NAME: dict[str, BaseTool] = {tool_obj.name: tool_obj for tool_obj in TOOLS}
TOOLS_BY_NAME_MENU: dict[str, BaseTool] = {
    tool_obj.name: tool_obj for tool_obj in TOOLS_MENU
}

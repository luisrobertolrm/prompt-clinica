from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import datetime, time, timedelta

from langchain.tools import BaseTool, tool
from rich import print
from sqlalchemy import select
from sqlalchemy.engine.url import make_url

from db import get_session
from ia.state import (
    AgendaProcedimento,
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


@tool
def consultar_agenda_disponibilidade(
    id_especialidade_procedimento: int, tipo: int
) -> list[DisponibilidadeAgenda]:
    """Lista slots disponíveis nas próximas duas semanas em blocos de 20 minutos.

    Args:
        id_especialidade_procedimento: identificador da especialidade (tipo=1) ou procedimento (tipo=2).
        tipo: 1 para especialidade, 2 para procedimento.
    Return:
        Lista de DisponibilidadeAgenda com horário, médico e tipo.
    """
    hoje = datetime.now().date()
    limite = hoje + timedelta(days=14)
    duracao_minutos = 20

    print("chamou consultar_agenda_disponibilidade")
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
            DisponibilidadeMedico.data_inicio <= limite,
            DisponibilidadeMedico.data_fim >= hoje,
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
                            )
                        )
                        horario_atual += timedelta(minutes=duracao_minutos)

                dia_atual += timedelta(days=1)

    slots.sort(key=lambda item: (item.data, item.id_medico))
    return slots


@tool
def marcar_consulta_procedimento(
    id_paciente: int,
    id_medico: int,
    dia: datetime,
    id_especialidade_procedimento: int,
    tipo: int,
) -> AgendaProcedimento:
    """
    Marca um procedimento para o paciente.

    Args:
        id_paciente: identificador do paciente.
        dia: data/hora desejada (datetime ou Date).
        id_especialidade_procedimento: identificador da especialidade médica.
        tipo: identificador do procedimento.
    Return:
        AgendaProcedimento com dados simulados da agenda.
    """
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

            return AgendaProcedimento(
                data=dia,
                id_agenda=1,
                id_especialidade=id_especialidade_procedimento,
                id_procedimento=None,
            )
    else:
        with get_session() as session:
            repo = Repository(session, Procedimento)
            return AgendaProcedimento(
                data=dia,
                id_agenda=1,
                id_especialidade=id_especialidade_procedimento,
                id_procedimento=None,
            )

            # procedimento = Procedimento(
            #     id_funcionario=1,
            #     id_medico=id_medico,
            #     id_paciente=id_paciente,
            #     id_tipo_especialidade=id_especialidade_procedimento,
            #     data_consulta=dia,
            #     data_criacao=datetime.now(),
            #     observacao=None,
            # )


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
    return Cliente(cpf=cpf, nome="Joao da Silva", id_usuario=1).as_dict()


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
def consultar_especialidade_procedimento(especialidade: str):
    """
    Lista especialidades/procedimentos disponíveis.

    Args:
        especialidade: texto para filtragem (não aplicado nesta simulação).
    Return:
        Lista simulada de EspecialidadeProcedimento.
    """
    with get_session() as session:
        repo_espec = Repository(session, TipoEspecialidade)
        repo_proc = Repository(session, Procedimento)

        filtro_esp = TipoEspecialidade.descricao.ilike(f"%{especialidade}%")
        especialidades = list(repo_espec.select(filtro_esp))

        filtro_proc = Procedimento.tipo_procedimento.has(
            TipoProcedimento.descricao.ilike(f"%{especialidade}%")
        )
        procedimentos = list(repo_proc.select(filtro_proc))

        retorno: list[EspecialidadeProcedimento] = [
            EspecialidadeProcedimento(
                id_especialidade_procedimento=esp.id,
                nome=esp.descricao,
                tipo=1,
            )
            for esp in especialidades
        ] + [
            EspecialidadeProcedimento(
                id_especialidade_procedimento=proc.id_tipo_procedimento,
                nome=proc.tipo_procedimento.descricao,
                tipo=2,
            )
            for proc in procedimentos
            if proc.tipo_procedimento is not None
        ]

    return retorno


TOOLS: Sequence[BaseTool] = [
    marcar_consulta_procedimento,
    desmarcar_consulta_procedimento,
    confirmar_consulta_procedimento,
    consular_consulta_procedimento,
    cadastrar_alterar_cliente,
    consultar_cliente,
    consultar_especialidade_procedimento,
    consultar_agenda_disponibilidade,
]

TOOLS_BY_NAME: dict[str, BaseTool] = {tool_obj.name: tool_obj for tool_obj in TOOLS}

import json
from collections.abc import Sequence
from typing import Any, Literal

from langchain.tools import BaseTool
from langchain_core.messages import SystemMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import ValidationError

from .llm_config import create_llm
from .prompt import (
    SYSTEM_MESSASE_CONFIRMAR_CONSULTA,
    SYSTEM_MESSASE_DESMARCAR_CONSULTA,
    SYSTEM_MESSASE_MARCAR_CONSULTA,
    SYSTEM_MESSASE_MARCAR_PROCEDIMENTO,
)
from .state import AgendaConsulta, AgendaProcedimento, Cliente, State, StateAgendamento
from .tools import (
    TOOLS,
    TOOLS_CONFIRMAR_CONSULTA,
    TOOLS_CONSULTAR_AGENDA,
    TOOLS_CONSULTAR_ESPECIALIDADES,
    TOOLS_DESMARCAR_CONSULTA,
    TOOLS_MARCAR_CONSULTA,
    TOOLS_MARCAR_PROCEDIMENTO,
    TOOLS_MENU,
)


def execute_llm(state: State) -> State:
    llm = create_llm().bind_tools(TOOLS)
    resp_llm = llm.invoke(state["messages"])
    return {"messages": [resp_llm], "paciente": state.get("paciente")}


node_tool = ToolNode(TOOLS)

def executou_consulta(state:State)  -> Literal["SIM", "NAO"]:
    retorno = "NAO"
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, ToolMessage) and msg.name in {
            "consultar_cliente"
        }:
            retorno = "SIM"
            break

    return retorno


def atualizar_state_paciente_node(state: State) -> State:
    """Atualiza state['paciente'] com o retorno das ferramentas de cliente."""

    def _extract_payload(msg: ToolMessage) -> Any | None:
        payload = msg.content
        if payload is None:
            return None
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError as err:
                print(f"Falha ao decodificar JSON ({err}): {payload}")
                return None
        return None

    payload: Any | None = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, ToolMessage) and msg.name in {
            "consultar_cliente",
            "cadastrar_alterar_cliente",
        }:
            payload = _extract_payload(msg)
            break

    if payload is None:
        return {"messages": state["messages"], "paciente": None}

    try:
        cliente = Cliente(
            cpf=str(payload.get("cpf", "")),
            nome=str(payload.get("nome", "")),
            sexo=payload.get("sexo"),
            email=payload.get("email"),
            data_nascimento=payload.get("data_nascimento"),
            id_usuario=payload.get("id_usuario"),
        )
    except (ValidationError, ValueError, TypeError):
        print("[bold red]Dados do cliente inválidos ou incompletos:", payload)
        return {"messages": state["messages"], "paciente": None}

    return {"messages": state["messages"], "paciente": cliente}


def configure_graph_cadastro() -> CompiledStateGraph:
    config_graph = StateGraph(State)

    config_graph.add_node("execute_llm", execute_llm)
    config_graph.add_node("tools", node_tool)
    config_graph.add_node("atualizar_state_paciente", atualizar_state_paciente_node)



    config_graph.add_edge(START, "execute_llm")
    config_graph.add_conditional_edges("execute_llm", tools_condition, ["tools", END])
    config_graph.add_edge("tools", "atualizar_state_paciente")
    config_graph.add_conditional_edges("atualizar_state_paciente", executou_consulta,
                                       {
                                           "SIM":"execute_llm",
                                           "NAO":END
                                       })
    #config_graph.add_edge("atualizar_state_paciente", END)

    return config_graph.compile(checkpointer=InMemorySaver())


def _atualizar_agendamento_node(state: StateAgendamento) -> StateAgendamento:
    """Extrai o resultado de marcar_consulta_procedimento e salva em state['agendamento']."""

    def _extract_payload(msg: ToolMessage) -> Any | None:
        payload = msg.content
        if payload is None:
            return None
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return None
        return None

    payload: Any | None = None
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, ToolMessage) and msg.name == "marcar_consulta_procedimento":
            payload = _extract_payload(msg)
            break

    if payload is None:
        return {**state, "agendamento": None}

    try:
        if "id_consulta" in payload:
            agendamento: AgendaConsulta | AgendaProcedimento = AgendaConsulta(**payload)
        else:
            agendamento = AgendaProcedimento(**payload)
    except (ValidationError, ValueError, TypeError):
        return {**state, "agendamento": None}

    return {**state, "agendamento": agendamento}


def _build_agendamento_graph(tools: Sequence[BaseTool], system_message: str) -> CompiledStateGraph:
    """Constrói graph usando StateAgendamento (opções marcar consulta/procedimento)."""

    def _execute_llm(state: StateAgendamento) -> StateAgendamento:
        llm = create_llm().bind_tools(tools)
        messages = state["messages"]
        if system_message and not any(
            isinstance(m, SystemMessage) and m.content == system_message
            for m in messages
        ):
            messages = [SystemMessage(system_message), *messages]
        resp_llm = llm.invoke(messages)
        return {**state, "messages": [resp_llm]}

    tool_node = ToolNode(tools)

    def _after_tools(state: StateAgendamento) -> StateAgendamento:
        updated = _atualizar_agendamento_node(state)
        return _execute_llm(updated)

    config_graph = StateGraph(StateAgendamento)
    config_graph.add_node("execute_llm", _execute_llm)
    config_graph.add_node("tools", tool_node)
    config_graph.add_node("after_tools", _after_tools)

    config_graph.add_edge(START, "execute_llm")
    config_graph.add_conditional_edges("execute_llm", tools_condition, ["tools", END])
    config_graph.add_edge("tools", "after_tools")
    config_graph.add_conditional_edges("after_tools", tools_condition, ["tools", END])

    return config_graph.compile(checkpointer=InMemorySaver())


def _build_graph(tools: Sequence[BaseTool], system_message: str) -> CompiledStateGraph:
    """Constrói graph padrão de menu usando State."""

    def _execute_llm(state: State) -> State:
        llm = create_llm().bind_tools(tools)
        messages = state["messages"]
        if system_message and not any(
            isinstance(m, SystemMessage) and m.content == system_message
            for m in messages
        ):
            messages = [SystemMessage(system_message), *messages]
        resp_llm = llm.invoke(messages)
        return {"messages": [resp_llm], "paciente": state.get("paciente")}

    config_graph = StateGraph(State)
    config_graph.add_node("execute_llm_menu", _execute_llm)
    config_graph.add_node("tools", ToolNode(tools))

    config_graph.add_edge(START, "execute_llm_menu")
    config_graph.add_conditional_edges(
        "execute_llm_menu", tools_condition, ["tools", END]
    )
    config_graph.add_edge("tools", "execute_llm_menu")

    return config_graph.compile(checkpointer=InMemorySaver())


_OPCAO_CONFIG: dict[int, tuple[Sequence[BaseTool], str, bool]] = {
    1: (TOOLS_MARCAR_CONSULTA,          SYSTEM_MESSASE_MARCAR_CONSULTA,      True),
    2: (TOOLS_MARCAR_PROCEDIMENTO,      SYSTEM_MESSASE_MARCAR_PROCEDIMENTO,  True),
    3: (TOOLS_CONSULTAR_AGENDA,         "",                                  False),
    4: (TOOLS_DESMARCAR_CONSULTA,       SYSTEM_MESSASE_DESMARCAR_CONSULTA,   False),
    5: (TOOLS_CONFIRMAR_CONSULTA,       SYSTEM_MESSASE_CONFIRMAR_CONSULTA,   True),
    6: (TOOLS_CONSULTAR_ESPECIALIDADES, "",                                  False),
}


def graph_factory(opcao: int) -> CompiledStateGraph:
    """Retorna o graph compilado para a opção do menu.

    Opções 1 e 2 usam StateAgendamento com system message embutida;
    demais usam State.

    Args:
        opcao: número da opção escolhida no menu (1-6).
    Return:
        Graph compilado pronto para uso.
    """
    tools, system_message, usa_agendamento = _OPCAO_CONFIG.get(
        opcao, (TOOLS_MENU, "", False)
    )

    if usa_agendamento:
        return _build_agendamento_graph(tools, system_message)

    return _build_graph(tools, system_message)

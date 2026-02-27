import json
from typing import Any

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import ValidationError

from .state import Cliente, State
from .tools import TOOLS, TOOLS_MENU


# model="gpt-4.1-mini",
#     temperature=0.0,
#     max_output_tokens=200,
def create_llm() -> BaseChatModel:
    # Modelo anterior não existe na API; usar um ID válido do OpenAI
    return init_chat_model(model="gpt-4.1-mini")


def execute_llm(state: State) -> State:
    llm = create_llm().bind_tools(TOOLS)

    last_message = state["messages"][-1]
    resp_llm = llm.invoke(state["messages"])
    return {"messages": [resp_llm], "paciente": state.get("paciente")}


def execute_llm_menu(state: State) -> State:
    llm = create_llm().bind_tools(TOOLS_MENU)

    last_message = state["messages"][-1]
    resp_llm = llm.invoke(state["messages"])
    return {"messages": [resp_llm], "paciente": state.get("paciente")}


node_tool = ToolNode(TOOLS)
node_tool_menu = ToolNode(TOOLS_MENU)


def atualizar_state_paciente_node(state: State) -> State:
    """Atualiza state['paciente'] com o retorno das ferramentas de cliente.

    Procura a última ToolMessage com nome consultar_cliente ou
    cadastrar_alterar_cliente e preenche o cliente no estado. Se a
    ferramenta retornar None ou dados inválidos, limpa o paciente.
    """

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
    config_graph.add_edge("atualizar_state_paciente", END)

    return config_graph.compile(checkpointer=InMemorySaver())


def configure_graph_menu() -> CompiledStateGraph:
    config_graph = StateGraph(State)

    config_graph.add_node("execute_llm_menu", execute_llm_menu)
    config_graph.add_node("tools", node_tool_menu)

    config_graph.add_edge(START, "execute_llm_menu")
    config_graph.add_conditional_edges(
        "execute_llm_menu", tools_condition, ["tools", END]
    )
    config_graph.add_edge("execute_llm_menu", END)

    return config_graph.compile(checkpointer=InMemorySaver())

from langchain.chat_models import BaseChatModel, init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from .state import State
from .tools import TOOLS


def create_llm() -> BaseChatModel:
    # Modelo anterior não existe na API; usar um ID válido do OpenAI
    return init_chat_model("gpt-3.5-turbo")


def execute_llm(state: State) -> State:
    llm = create_llm()

    last_message = state["messages"][-1]
    resp_llm = llm.invoke(state["messages"])
    return {"messages": [resp_llm]}


node_tool = ToolNode(TOOLS)


def configure_graph() -> CompiledStateGraph:
    config_graph = StateGraph(State)

    config_graph.add_node("execute_llm", execute_llm)
    config_graph.add_node("tools", node_tool)

    config_graph.add_edge(START, "execute_llm")
    config_graph.add_conditional_edges("execute_llm", tools_condition, ["tools", END])
    config_graph.add_edge("tools", "execute_llm")

    return config_graph.compile(checkpointer=InMemorySaver())

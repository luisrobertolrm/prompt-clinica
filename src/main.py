import sys
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from rich import print

# from langchain_core.tracers.stdout import FunctionCallbackHandler
from rich.prompt import Prompt

from ia.state import Cliente, State

# Garante que o projeto raiz esteja no sys.path para importar db.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ia.graph import configure_graph_cadastro, configure_graph_menu
from ia.prompt import SYSTEM_MESSAGE, SYSTEM_MESSAGE_CADASTRO


def recuperar_cliente() -> str | None:
    config = RunnableConfig(configurable={"thread_id": 1})
    graph = configure_graph_cadastro()

    current_messages = []
    prompt = Prompt()

    while True:
        text = prompt.ask("[bold cyan]Você:")

        if text.lower() in ["sair", "quit", "exit"]:
            print("Saindo ✋✋✋")
            break

        paciente: Cliente | None | str = None
        msg = HumanMessage(content=text)

        if len(current_messages) == 0:
            current_messages = [SystemMessage(SYSTEM_MESSAGE_CADASTRO), msg]
        else:
            current_messages = [msg]

        resp_llm = graph.invoke(State(messages=current_messages), config=config)

        try:
            paciente = resp_llm.get("paciente")
            if isinstance(paciente, Cliente):
                return paciente.model_dump_json()
            print(resp_llm["messages"][-1].content)

        except Exception as err:
            print(resp_llm["messages"][-1].content)


def main():
    config = RunnableConfig(configurable={"thread_id": 2})
    prompt = Prompt()
    current_messages = []

    paciente = recuperar_cliente()
    graph = configure_graph_menu()

    if paciente is None:
        print(
            "[bold red]Não foi possível recuperar os dados do cliente. Encerrando o programa."
        )
        return

    while True:
        if len(current_messages) == 0:
            msg = HumanMessage("Apresente o menu")
            current_messages = [
                SystemMessage(SYSTEM_MESSAGE),
                SystemMessage("Sempre tratar o paciente pelo nome"),
                SystemMessage("Dados do paciente = " + paciente),
                msg,
            ]
        else:
            text = prompt.ask("[bold cyan]Você:")
            if text.lower() in ["sair", "quit", "exit"]:
                print("Saindo ✋✋✋")
                break
            msg = HumanMessage(content=text)
            current_messages = [msg]

        resp_menu = graph.invoke(State(messages=current_messages), config=config)

        print(resp_menu["messages"][-1].content)

        print(resp_menu)


if __name__ == "__main__":
    main()

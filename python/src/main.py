import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from rich import print
from rich.prompt import Prompt

from core_logic import MENU_OPCOES, identificar_opcao_menu
from ia.cadastro_handler import CadastroHandler
from ia.graph import graph_factory
from ia.state import State


def exibir_menu() -> int:
    prompt = Prompt()

    print(f"[bold yellow]O que você deseja?{MENU_OPCOES}")

    while True:
        text: str = prompt.ask("[bold cyan]Você:")

        if text.strip().lower() in ["sair", "quit", "exit"]:
            return 0

        opcao = identificar_opcao_menu(text)

        if opcao is not None:
            return opcao

        print(f"[bold yellow]Não entendi. Por favor, escolha uma das opções:{MENU_OPCOES}")


def recuperar_cliente() -> str | None:
    handler = CadastroHandler(thread_id=1)
    prompt = Prompt()

    while True:
        text: str = prompt.ask("[bold cyan]Você:")

        if text.lower() in ["sair", "quit", "exit"]:
            print("Saindo ✋✋✋")
            break

        response = handler.processar_mensagem(text)

        if response.cliente is not None:
            return response.cliente.model_dump_json()

        print(response.messages[-1].content)

    return None


def main() -> None:
    config = RunnableConfig(configurable={"thread_id": 2})
    prompt = Prompt()
    current_messages: list[SystemMessage | HumanMessage] = []

    paciente: str | None = recuperar_cliente()

    if paciente is None:
        print("[bold red]Não foi possível recuperar os dados do cliente. Encerrando o programa.")
        return

    opcao_escolhida: int = exibir_menu()
    graph = graph_factory(opcao_escolhida)

    while True:
        if len(current_messages) == 0:
            current_messages = [
                SystemMessage("Sempre tratar o paciente pelo nome"),
                SystemMessage("Dados do paciente = " + paciente),
            ]
        else:
            text: str = prompt.ask("[bold cyan]Você:")
            if text.lower() in ["sair", "quit", "exit"]:
                print("Saindo ✋✋✋")
                break
            current_messages = [HumanMessage(content=text)]

        resp_menu = graph.invoke(State(messages=current_messages), config=config)
        print(resp_menu["messages"][-1].content)


if __name__ == "__main__":
    main()

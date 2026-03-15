import sys
from pathlib import Path

# Garante que o projeto raiz esteja no sys.path para importar db.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from rich import print
from rich.prompt import Prompt

from ia.cadastro_handler import CadastroHandler
from ia.graph import configure_graph_menu, create_llm
from ia.prompt import SYSTEM_MESSAGE
from ia.state import State

MENU_OPCOES = """
1 - Marcar Consulta
2 - Marcar Procedimento
3 - Consultar Agenda
4 - Desmarcar Consulta
5 - Confirmar Consulta
6 - Consultar Especialidades Disponíveis
"""

MENU_SYSTEM = (
    "Você interpreta a intenção do usuário e retorna APENAS o número da opção "
    "correspondente ao menu abaixo, sem texto adicional.\n"
    + MENU_OPCOES
    + "Se não conseguir identificar a opção, retorne 0."
)


def exibir_menu() -> int:
    llm = create_llm()
    prompt = Prompt()

    print(f"[bold yellow]O que você deseja?{MENU_OPCOES}")

    while True:
        text = prompt.ask("[bold cyan]Você:")

        if text.strip().lower() in ["sair", "quit", "exit"]:
            return 0

        resposta = llm.invoke([
            SystemMessage(MENU_SYSTEM),
            HumanMessage(text),
        ])

        conteudo: str = str(resposta.content).strip()

        if conteudo.isdigit() and 1 <= int(conteudo) <= 6:
            return int(conteudo)

        print(f"[bold yellow]Não entendi. Por favor, escolha uma das opções:{MENU_OPCOES}") a respota
    Retornar 


def recuperar_cliente() -> str | None:
    handler = CadastroHandler(thread_id=1)
    prompt = Prompt()

    while True:
        text = prompt.ask("[bold cyan]Você:")

        if text.lower() in ["sair", "quit", "exit"]:
            print("Saindo ✋✋✋")
            break

        response = handler.processar_mensagem(text)

        if response.cliente is not None:
            return response.cliente.model_dump_json()

        print(response.messages[-1].content)


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


if __name__ == "__main__":
    main()

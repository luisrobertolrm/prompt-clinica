from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

# from langchain_core.tracers.stdout import FunctionCallbackHandler
from rich.prompt import Prompt

from ia.graph import configure_graph
from ia.prompt import SYSTEM_MESSAGE


def main():
    # fn_handler_cb = FunctionCallbackHandler(function=print)
    config = RunnableConfig(configurable={"thread_id": 1})
    graph = configure_graph()

    current_messages = []

    prompt = Prompt()

    while True:
        text = prompt.ask("[bold cyan]Você:")

        if text.lower() in ["sair", "quit", "exit"]:
            print("Saindo ✋✋✋")
            break

        msg = HumanMessage(content=text)

        if len(current_messages) == 0:
            current_messages = [SystemMessage(SYSTEM_MESSAGE), msg]
        else:
            current_messages = [msg]

        resp_llm = graph.invoke({"messages": current_messages}, config=config)

        print(resp_llm["messages"][-1].content)


if __name__ == "__main__":
    main()

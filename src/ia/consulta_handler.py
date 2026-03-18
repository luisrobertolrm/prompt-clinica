from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from .graph import configure_graph_cadastro
from .prompt import SYSTEM_MESSAGE_CADASTRO
from .state import Cliente, State


@dataclass
class CadastroResponse:
    """Resposta do handler de cadastro contendo mensagens e dados do cliente."""

    messages: list[BaseMessage]
    cliente: Cliente | None


class ConsultaHandler:
    """Gerencia o fluxo de marcação de consulta de cliente via LangGraph."""

    def __init__(self, thread_id: int = 1) -> None:
        self.config: RunnableConfig = RunnableConfig(
            configurable={"thread_id": thread_id}
        )
        self.graph = configure_graph_cadastro()
        self.is_first_interaction: bool = True

    def processar_mensagem(self, mensagem_usuario: str) -> CadastroResponse:
        """
        Processa uma mensagem do usuário e retorna resposta com dados do cliente.

        Args:
            mensagem_usuario: Texto enviado pelo usuário

        Returns:
            CadastroResponse com mensagens e cliente (se encontrado/cadastrado)
        """
        msg = HumanMessage(content=mensagem_usuario)

        if self.is_first_interaction:
            current_messages = [SystemMessage(SYSTEM_MESSAGE_CADASTRO), msg]
            self.is_first_interaction = False
        else:
            current_messages = [msg]

        resp_llm = self.graph.invoke(
            State(messages=current_messages), config=self.config
        )

        paciente = resp_llm.get("paciente")
        cliente: Cliente | None = None

        if isinstance(paciente, Cliente):
            cliente = paciente

        return CadastroResponse(
            messages=resp_llm["messages"],
            cliente=cliente,
        )

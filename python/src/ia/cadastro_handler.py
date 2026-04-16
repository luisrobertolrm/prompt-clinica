import re
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from .graph import configure_graph_cadastro
from .prompt import SYSTEM_MESSAGE_CADASTRO
from .state import Cliente, State


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF seguindo as regras de módulo 11."""
    # Remove formatações se houver
    cpf_limpo = re.sub(r'[^0-9]', '', str(cpf))

    # Descarta se não for numérico (após limpeza) ou se não tiver 11 dígitos
    if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
        return False

    # Exclui CPFs com todos os dígitos iguais (ex: 00000000000, 11111111111)
    if cpf_limpo == cpf_limpo[0] * 11:
        return False

    # Validação do primeiro dígito verificador (Módulo 11)
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito_1 = 0 if resto == 10 else resto

    if int(cpf_limpo[9]) != digito_1:
        return False

    # Validação do segundo dígito verificador (Módulo 11)
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito_2 = 0 if resto == 10 else resto

    if int(cpf_limpo[10]) != digito_2:
        return False

    return True


@dataclass
class CadastroResponse:
    """Resposta do handler de cadastro contendo mensagens e dados do cliente."""

    messages: list[BaseMessage]
    cliente: Cliente | None
    consultouCliente: bool = False
    cadastrouCliente:bool = False


class CadastroHandler:
    """Gerencia o fluxo de cadastro/recuperação de cliente via LangGraph."""

    def __init__(self, thread_id: int = 1) -> None:
        self.config: RunnableConfig = RunnableConfig(
            configurable={"thread_id": thread_id}
        )
        self.graph = configure_graph_cadastro()
        self.is_first_interaction: bool = True

    def processar_mensagem(self, mensagem_usuario: str, history: list | None = None) -> CadastroResponse:
        """
        Processa uma mensagem do usuário e retorna resposta com dados do cliente.

        Args:
            mensagem_usuario: Texto enviado pelo usuário
            history: Opcional histórico (para sistemas sem estado como REST API)

        Returns:
            CadastroResponse com mensagens e cliente (se encontrado/cadastrado)
        """
        from langchain_core.messages import AIMessage
        
        current_messages = []
        if self.is_first_interaction:
            current_messages.append(SystemMessage(SYSTEM_MESSAGE_CADASTRO))
            self.is_first_interaction = False

        if history:
            for m in history:
                role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else None)
                content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else None)
                
                if role in ["user", "human"]:
                    current_messages.append(HumanMessage(content=content))
                elif role in ["assistant", "ai"]:
                    current_messages.append(AIMessage(content=content))
                elif role == "system":
                    current_messages.append(SystemMessage(content=content))

        current_messages.append(HumanMessage(content=mensagem_usuario))

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

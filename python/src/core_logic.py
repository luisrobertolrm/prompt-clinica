from langchain_core.messages import HumanMessage, SystemMessage

from ia.graph import create_llm

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

def identificar_opcao_menu(texto: str) -> int | None:
    """Invoca o LLM para classificar a intenção do usuário e retornar o menu."""
    llm = create_llm()
    resposta = llm.invoke([
        SystemMessage(MENU_SYSTEM),
        HumanMessage(texto),
    ])

    conteudo: str = str(resposta.content).strip()

    if conteudo.isdigit() and 1 <= int(conteudo) <= 6:
        return int(conteudo)

    return None

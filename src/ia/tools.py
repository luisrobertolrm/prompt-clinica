from collections.abc import Sequence

from langchain.tools import BaseTool, tool


class Pessoa:
    def __init__(self, cpf: str, nome: str, rg: str) -> None:
        self.cpf = cpf
        self.nome = nome
        self.rg = rg

    def as_dict(self) -> dict[str, str]:
        return {"cpf": self.cpf, "nome": self.nome, "rg": self.rg}


@tool
def marcar_consulta(id_usuario: int, data: str, especialidade: str) -> dict[str, str]:
    """
    Marca consulta para o cliente.
    Args:
        id_usuario - (int) id retornado de pesquisar_pessoa
        data - (str, ISO ou dd/mm/aaaa) data do exame
        especialidade - (str) especialidade médica, p.ex. "clinica geral"
    Return: dict com 'id_usuario', 'data', 'especialidade', 'medico'
    """
    return {
        "id_usuario": str(id_usuario),
        "data": data,
        "especialidade": especialidade,
        "medico": "Antônio Duarte",
    }


@tool
def marcar_procedimento(
    id_usuario: int, data: str, procedimento: str
) -> dict[str, str]:
    """
    Marca procedimento para o cliente, p.ex. "Biópsia", "Cateterismo".
    Args:
        id_usuario - (int) id retornado de pesquisar_pessoa
        data - (str, ISO ou dd/mm/aaaa) data do procedimento
        procedimento - (str) descrição do procedimento
    Return: dict com 'id_usuario', 'procedimento', 'data', 'horario', 'medico'
    """
    return {
        "id_usuario": str(id_usuario),
        "procedimento": procedimento,
        "horario": "15:00",
        "data": data,
        "medico": "Antônio Duarte",
    }


@tool
def confirmar(id_usuario: int, proced_consulta: str) -> str:
    """
    Confirma se há procedimento ou consulta marcada e retorna um resumo.
    Args:
        id_usuario - (int) id retornado de pesquisar_pessoa
        proced_consulta - (str) nome da consulta ou do procedimento a confirmar
    Return: mensagem textual confirmando ou não
    """
    return f"{proced_consulta} do usuário {id_usuario} confirmada para 01/01/2027 às 15:00."


@tool
def pesquisar_pessoa(cpf: str) -> dict[str, str] | None:
    """
    Procura uma pessoa pelo cpf em uma base de dados e retorna o nome e o rg.
    Args:
        cpf - (str): O cpf da pessoa a ser procurada.
    Returns:     caso não encontre retorna None, caso encontre um dicionário com as propriedade nome e rg
    """
    if cpf == "12345678900":
        return Pessoa(cpf, "João da Silva", "MG-12.345.678").as_dict()
    if cpf == "98765432100":
        return Pessoa(cpf, "Maria Souza", "SP-98.765.432").as_dict()
    return None


@tool
def opcao_usuarios() -> dict[int, str]:
    """
    Opções que o usuário pode fazer no sistema.
    Return: dict[int, str] com as opções do menu e a tool correspondente
    """
    return {
        1: "Marcar Consulta [tool: marcar_consulta]",
        2: "Marcar Procedimento [tool: marcar_procedimento]",
        3: "Confirmar Consulta ou Procedimento [tool: confirmar]",
    }


TOOLS: Sequence[BaseTool] = [
    marcar_consulta,
    marcar_procedimento,
    confirmar,
    pesquisar_pessoa,
    opcao_usuarios,
]

TOOLS_BY_NAME: dict[str, BaseTool] = {tool_obj.name: tool_obj for tool_obj in TOOLS}

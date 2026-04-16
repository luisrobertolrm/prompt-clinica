
from fastapi import FastAPI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from core_logic import MENU_OPCOES, identificar_opcao_menu
from ia.cadastro_handler import CadastroHandler
from ia.graph import graph_factory
from ia.state import State

app = FastAPI(
    title="Clínica AI REST API", description="API para Atendimento Clínico (LangGraph)"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", or "system"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    paciente: str | None = None
    opcao_escolhida: int | None = None
    thread_id: int = 2


class ChatResponse(BaseModel):
    response: str
    paciente: str | None = None
    opcao_escolhida: int | None = None


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    # Fase 1: Cadastro do Paciente
    if not req.paciente:
        handler = CadastroHandler(thread_id=req.thread_id)
        response = handler.processar_mensagem(req.message, req.history)
        if response.cliente is not None:
            # Paciente cadastrado com sucesso!
            return ChatResponse(
                response=f"O que você deseja?\n{MENU_OPCOES}",
                paciente=response.cliente.model_dump_json(),
            )
        # Ainda em processo de cadastro
        return ChatResponse(response=str(response.messages[-1].content))

    # Fase 2: Seleção do Menu
    if req.opcao_escolhida is None or req.opcao_escolhida == 0:
        opcao = identificar_opcao_menu(req.message)

        if opcao is not None:
            # Opção identificada! Inicializar o fluxo com o prompt do sistema
            graph = graph_factory(opcao)
            config = RunnableConfig(configurable={"thread_id": req.thread_id})

            langchain_messages = []
            langchain_messages.append(SystemMessage("Sempre tratar o paciente pelo nome"))
            langchain_messages.append(SystemMessage("Dados do paciente = " + req.paciente))

            for msg in req.history:
                if msg.role in ["user", "human"]:
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role in ["assistant", "ai"]:
                    langchain_messages.append(AIMessage(content=msg.content))
                elif msg.role == "system":
                    langchain_messages.append(SystemMessage(content=msg.content))

            langchain_messages.append(HumanMessage(content=req.message))

            result = graph.invoke(State(messages=langchain_messages), config=config)

            return ChatResponse(
                response=str(result["messages"][-1].content),
                paciente=req.paciente,
                opcao_escolhida=opcao,
            )
        return ChatResponse(
            response=f"Não entendi. Por favor, escolha uma das opções:\n{MENU_OPCOES}",
            paciente=req.paciente,
        )

    # Fase 3: Fluxo da Opção Escolhida (Graph)
    graph = graph_factory(req.opcao_escolhida)
    config = RunnableConfig(configurable={"thread_id": req.thread_id})

    # Reconstruindo o histórico para o LangGraph (state stateless reconstruído pelo payload)
    langchain_messages = []
    langchain_messages.append(SystemMessage("Sempre tratar o paciente pelo nome"))
    langchain_messages.append(SystemMessage("Dados do paciente = " + req.paciente))

    for msg in req.history:
        if msg.role in ["user", "human"]:
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role in ["assistant", "ai"]:
            langchain_messages.append(AIMessage(content=msg.content))
        elif msg.role == "system":
            langchain_messages.append(SystemMessage(content=msg.content))

    langchain_messages.append(HumanMessage(content=req.message))

    result = graph.invoke(State(messages=langchain_messages), config=config)

    return ChatResponse(
        response=str(result["messages"][-1].content),
        paciente=req.paciente,
        opcao_escolhida=req.opcao_escolhida,
    )

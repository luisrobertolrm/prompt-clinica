import os

from rich import print
from sqlalchemy.engine.url import make_url

from db import get_session
from models.entities import TipoEspecialidade
from repositories import Repository

raw_url = os.getenv("DATABASE_URL", "")
if raw_url:
    masked_url = make_url(raw_url).set(password="***")
    print("DATABASE_URL:", masked_url)

with get_session() as session:
    tipos_esp = Repository(session, TipoEspecialidade)

    # SELECT
    cadastrado = tipos_esp.list()

    for item in cadastrado:
        print(item)

    # INSERT
    # novo = tipos_esp.add(
    #     TipoEspecialidade(descricao="Pediatria", duracao_consulta_padrao=20)
    # )
    # print("Criado id:", novo.id)

    # # UPDATE
    # tipos_esp.update(novo.id, {"conteudo": b"conteudo atualizado"})
    # atualizado = tipos_esp.get(novo.id)
    # print("Conteudo apos update:", atualizado.conteudo)

    # DELETE
    # documentos.delete(novo.id)
    # print("Deletado?", documentos.get(novo.id) is None)

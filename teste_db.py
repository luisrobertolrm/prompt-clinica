from db import get_session
from repositories import Repository
from models.entities import Documento

with get_session() as session:
    documentos = Repository(session, Documento)

    # INSERT
    novo = documentos.add(Documento(conteudo=b"exemplo de binario"))
    print("Criado id:", novo.id)

    # UPDATE
    documentos.update(novo.id, {"conteudo": b"conteudo atualizado"})
    atualizado = documentos.get(novo.id)
    print("Conteudo apos update:", atualizado.conteudo)

    # DELETE
    #documentos.delete(novo.id)
    #print("Deletado?", documentos.get(novo.id) is None)
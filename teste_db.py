from db import get_session
from models.entities import TipoEspecialidade
from repositories import Repository

with get_session() as session:
    tipos_esp = Repository(session, TipoEspecialidade)

    # INSERT
    novo = tipos_esp.add(
        TipoEspecialidade(descricao="Pediatria", duracao_consulta_padrao=20)
    )
    print("Criado id:", novo.id)

    # # UPDATE
    # tipos_esp.update(novo.id, {"conteudo": b"conteudo atualizado"})
    # atualizado = tipos_esp.get(novo.id)
    # print("Conteudo apos update:", atualizado.conteudo)

    # DELETE
    # documentos.delete(novo.id)
    # print("Deletado?", documentos.get(novo.id) is None)

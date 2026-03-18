from __future__ import annotations

import json
import math
import unicodedata

from sqlalchemy import select

from db import get_session
from ia.llm_config import create_embeddings
from models import TipoEspecialidade


def _normalizar(texto: str) -> str:
    """Remove acentos para compatibilidade com o cliente HTTP do Google GenAI."""
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def gerar_rag_especialidades() -> None:
    """Gera e persiste embeddings para todos os registros de TipoEspecialidade."""
    embeddings = create_embeddings()
    with get_session() as session:
        especialidades = list(session.scalars(select(TipoEspecialidade)))
        textos: list[str] = [_normalizar(e.descricao) for e in especialidades]
        vetores: list[list[float]] = embeddings.embed_documents(textos)

        for especialidade, vetor in zip(especialidades, vetores, strict=True):
            especialidade.embedding = json.dumps(vetor)


def _cosseno(a: list[float], b: list[float]) -> float:
    dot: float = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a: float = math.sqrt(sum(x * x for x in a))
    norm_b: float = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def buscar_especialidades_similares(texto: str, top_k: int = 5) -> list[TipoEspecialidade]:
    """Retorna os top_k registros de TipoEspecialidade mais similares ao texto."""
    embeddings = create_embeddings()
    vetor_query: list[float] = embeddings.embed_query(_normalizar(texto))

    with get_session() as session:
        registros = list(session.scalars(select(TipoEspecialidade).where(TipoEspecialidade.embedding.isnot(None))))
        scored: list[tuple[float, TipoEspecialidade]] = [
            (_cosseno(vetor_query, json.loads(r.embedding)), r)  # type: ignore[arg-type]
            for r in registros
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

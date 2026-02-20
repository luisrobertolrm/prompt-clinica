"""Script simples para testar a conexao com o Postgres.

Passos para usar:
1) No PowerShell, defina a string de conexao em DATABASE_URL, por exemplo:
   $env:DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost:5432/GerardorFluxoCaixa"
   (se a senha tiver @, troque @ por %40)
2) Execute o script:
   uv run python scripts/check_db.py

O script tenta conectar e criar as tabelas definidas nos models. Se conectar e
criar sem erro, a configuracao esta OK.
"""

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Garante que o diretório raiz do projeto esteja no sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

from models import Base


def main() -> None:
	url = os.environ.get("DATABASE_URL")
	if not url:
		raise SystemExit("DATABASE_URL nao definido. Defina a variavel de ambiente e tente novamente.")

	engine = create_engine(url, echo=True)
	try:
		Base.metadata.create_all(bind=engine)
	except SQLAlchemyError as exc:
		raise SystemExit(f"Falha ao conectar ou criar tabelas: {exc}") from exc
	else:
		print("Conexao OK e schema validado/criado com sucesso.")


if __name__ == "__main__":
	main()
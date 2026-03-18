import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich import print
from rich.prompt import Prompt
from ia.rag.especialidade_rag import gerar_rag_especialidades

def main() -> None:
    prompt = Prompt()

    gerar_rag_especialidades()

    

if __name__ == "__main__":
    main()

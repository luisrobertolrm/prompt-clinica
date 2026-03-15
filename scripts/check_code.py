#!/usr/bin/env python3
"""Script para verificar erros no código sem executar."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Executa comando e retorna se teve sucesso."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print(f"\n✅ {description} - OK")
        return True
    print(f"\n❌ {description} - FALHOU")
    return False


def main() -> None:
    """Executa todas as verificações."""
    root = Path(__file__).parent.parent

    checks = [
        ([sys.executable, "-m", "pyright"], "Type Checking (Pyright)"),
        ([sys.executable, "-m", "ruff", "check", "."], "Linting (Ruff)"),
    ]

    results = []
    for cmd, desc in checks:
        success = run_command(cmd, desc)
        results.append((desc, success))

    print(f"\n{'='*60}")
    print("📊 RESUMO")
    print(f"{'='*60}\n")

    all_passed = True
    for desc, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {desc}")
        if not success:
            all_passed = False

    print(f"\n{'='*60}\n")

    if all_passed:
        print("🎉 Todos os checks passaram!")
        sys.exit(0)
    else:
        print("⚠️  Alguns checks falharam. Corrija os erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()

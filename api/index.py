"""Ponto de entrada da Vercel: expõe a aplicação Flask de src/app.py.

Os módulos do projeto (shared, login_cliente, perfil_cliente...) ficam dentro de
src/, então essa pasta precisa estar no caminho do Python antes do import.
A Vercel procura a variável "app" (uma aplicação WSGI) neste arquivo.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app import app  # noqa: E402,F401

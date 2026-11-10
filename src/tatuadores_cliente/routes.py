from flask import Blueprint, render_template

from shared.auth import cliente_required
from tatuadores_cliente.forms import filtros_das_fichas, listar_fichas

# Tela "Tatuadores" do cliente: lista de fichas, ANTES do agendamento.
bp = Blueprint(
    "tatuadores_cliente",
    __name__,
    static_folder="static",
    static_url_path="/static/tatuadores_cliente",
)


@bp.route("/cliente/tatuadores")
@cliente_required
def lista():
    try:
        fichas = listar_fichas()
        erro = None
    except Exception as exc:
        print(">>> ERRO AO LISTAR TATUADORES (FICHAS):", exc)
        fichas, erro = [], "Não foi possível carregar os tatuadores agora."
    return render_template(
        "tatuadores_cliente/tatuadores.html",
        fichas=fichas,
        filtros=filtros_das_fichas(fichas),
        erro=erro,
        ativo="tatuadores",
    )

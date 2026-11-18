import os

from flask import Blueprint, jsonify, render_template, request

from configuracoes_tatuador.forms import FAQ, alterar_senha_do_tatuador
from shared.auth import tatuador_logado, tatuador_required

# Configurações do tatuador: menu, alterar senha (Supabase Auth) e ajuda/FAQ.
bp = Blueprint(
    "configuracoes_tatuador",
    __name__,
    static_folder="static",
    static_url_path="/static/configuracoes_tatuador",
)


@bp.route("/tatuador/configuracoes")
@tatuador_required
def configuracoes():
    """Menu de preferências da conta do tatuador."""
    return render_template("configuracoes_tatuador/configuracoes.html", ativo="configuracoes")


@bp.route("/tatuador/configuracoes/senha")
@tatuador_required
def alterar_senha():
    return render_template("configuracoes_tatuador/senha.html", ativo="configuracoes")


@bp.route("/api/tatuador/senha", methods=["POST"])
@tatuador_required
def api_alterar_senha():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "errors": {"geral": "Requisição inválida."}}), 400

    tatuador = tatuador_logado()
    try:
        ok, errors, status = alterar_senha_do_tatuador(tatuador["id"], tatuador["email"], data)
    except Exception as exc:
        print(">>> ERRO AO ALTERAR SENHA DO TATUADOR:", exc)
        return jsonify({"success": False, "errors": {"geral": "Erro ao alterar a senha. Tente novamente."}}), 500

    if not ok:
        return jsonify({"success": False, "errors": errors}), status
    return jsonify({"success": True, "message": "Senha alterada com sucesso."})


@bp.route("/tatuador/configuracoes/ajuda")
@tatuador_required
def ajuda():
    return render_template(
        "configuracoes_tatuador/ajuda.html",
        ativo="configuracoes",
        faq=FAQ,
        suporte_email=os.environ.get("SUPORTE_EMAIL"),
    )
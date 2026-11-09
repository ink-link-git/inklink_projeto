import os

from flask import Blueprint, jsonify, render_template, request

from configuracoes_cliente.forms import FAQ, alterar_senha_do_cliente
from shared.auth import cliente_logado, cliente_required

# Configurações do cliente: menu, alterar senha (Supabase Auth) e ajuda/FAQ.
bp = Blueprint(
    "configuracoes_cliente",
    __name__,
    static_folder="static",
    static_url_path="/static/configuracoes_cliente",
)


@bp.route("/cliente/configuracoes")
@cliente_required
def configuracoes():
    """Menu de preferências da conta do cliente."""
    return render_template("configuracoes_cliente/configuracoes.html", ativo="configuracoes")


@bp.route("/cliente/configuracoes/senha")
@cliente_required
def alterar_senha():
    return render_template("configuracoes_cliente/senha.html", ativo="configuracoes")


@bp.route("/api/cliente/senha", methods=["POST"])
@cliente_required
def api_alterar_senha():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "errors": {"geral": "Requisição inválida."}}), 400

    cliente = cliente_logado()
    try:
        ok, errors, status = alterar_senha_do_cliente(cliente["id"], cliente["email"], data)
    except Exception as exc:
        print(">>> ERRO AO ALTERAR SENHA:", exc)
        return jsonify({"success": False, "errors": {"geral": "Erro ao alterar a senha. Tente novamente."}}), 500

    if not ok:
        return jsonify({"success": False, "errors": errors}), status
    return jsonify({"success": True, "message": "Senha alterada com sucesso."})


@bp.route("/cliente/configuracoes/ajuda")
@cliente_required
def ajuda():
    return render_template(
        "configuracoes_cliente/ajuda.html",
        ativo="configuracoes",
        faq=FAQ,
        suporte_email=os.environ.get("SUPORTE_EMAIL"),
    )

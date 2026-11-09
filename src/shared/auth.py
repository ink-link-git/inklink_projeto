from functools import wraps

from flask import flash, jsonify, redirect, request, session, url_for


def tatuador_logado():
    """Retorna os dados do tatuador da sessão (ou None)."""
    return session.get("tatuador")


def cliente_logado():
    """Retorna os dados do cliente da sessão (ou None)."""
    return session.get("cliente")


def _quer_json():
    return request.path.startswith("/api/")


def tatuador_required(view):
    """Só deixa passar quem entrou como tatuador."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not tatuador_logado():
            if _quer_json():
                return jsonify({"success": False, "errors": {"geral": "Faça login como tatuador."}}), 401
            flash("Você precisa fazer login primeiro.", "warning")
            return redirect(url_for("login_tatuador.login"))
        return view(*args, **kwargs)
    return wrapper


def cliente_required(view):
    """Só deixa passar quem entrou como cliente."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not cliente_logado():
            if _quer_json():
                return jsonify({"success": False, "errors": {"geral": "Faça login como cliente."}}), 401
            return redirect(url_for("login_cliente.login_cliente"))
        return view(*args, **kwargs)
    return wrapper

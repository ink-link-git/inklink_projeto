from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from login_cliente.forms import (
    autenticar_cliente,
    validar_dados_usuario,
    verificar_duplicidade,
    registrar_usuario,
)

# Blueprint do módulo. O static_url_path próprio evita conflito com os outros módulos.
bp = Blueprint(
    "login_cliente",
    __name__,
    static_folder="static",
    static_url_path="/static/login_cliente",
)


@bp.route("/")
def selecionar_perfil():
    """Tela inicial 'Quem é você?' (entrar ou criar conta)."""
    return render_template("login_cliente/perfil.html")


@bp.route("/cadastro/cliente")
def cadastro_cliente():
    """Formulário de cadastro do cliente."""
    return render_template("login_cliente/index.html")


@bp.route("/login/cliente")
def login_cliente():
    """Tela de login do cliente."""
    if "cliente" in session:
        return redirect(url_for("login_cliente.home_cliente"))
    return render_template("login_cliente/login.html")


@bp.route("/cliente/home")
def home_cliente():
    """Área do cliente (só para quem fez login)."""
    cliente = session.get("cliente")
    if not cliente:
        return redirect(url_for("login_cliente.login_cliente"))
    return render_template("login_cliente/home.html", cliente=cliente)


@bp.route("/logout/cliente")
def logout_cliente():
    session.pop("cliente", None)
    return redirect(url_for("login_cliente.selecionar_perfil"))


@bp.route("/api/login/cliente", methods=["POST"])
def entrar_cliente():
    """Recebe e-mail e senha, autentica no Supabase e abre a sessão do cliente."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    cliente, erro = autenticar_cliente(email, senha)
    if erro:
        return jsonify({"success": False, "errors": {"geral": erro}}), 401

    session["cliente"] = cliente
    return jsonify({"success": True, "redirect": url_for("login_cliente.home_cliente")})


@bp.route("/api/index", methods=["POST"])
def criar_conta():
    """Recebe dados do formulário, valida, registra no Auth e salva na tabela 'cliente'."""
    data = request.get_json(silent=True) or {}

    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip().lower()
    telefone = (data.get("telefone") or "").strip()
    cpf = (data.get("cpf") or "").strip()
    senha = data.get("senha") or ""
    confirmar = data.get("confirmar") or ""

    # --- 1. Validação de dados ---
    errors, cpf_digits, tel_digits = validar_dados_usuario(nome, email, telefone, cpf, senha, confirmar)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- 2. Checagem prévia de duplicidade ---
    try:
        duplicidade_errors = verificar_duplicidade(email, cpf_digits)
        if duplicidade_errors:
            return jsonify({"success": False, "errors": duplicidade_errors}), 409
    except Exception as exc:
        return jsonify({"success": False, "errors": {"geral": str(exc)}}), 500

    # --- 3 & 4. Registro no Auth e salvamento na tabela ---
    try:
        registrar_usuario(email, senha, nome, cpf_digits, tel_digits)
    except Exception as exc:
        error_msg = str(exc)
        if "User already registered" in error_msg:
            return jsonify({"success": False, "errors": {"email": "Este e-mail já está cadastrado."}}), 400

        if "autenticação" in error_msg.lower():
            return jsonify({"success": False, "errors": {"geral": f"Erro na autenticação: {error_msg}"}}), 400

        return jsonify({
            "success": False,
            "errors": {"geral": f"Conta criada no Auth, mas falhou ao salvar perfil: {error_msg}"}
        }), 500

    return jsonify({"success": True, "usuario": {"nome": nome, "email": email}}), 201

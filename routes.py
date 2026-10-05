from flask import Blueprint, jsonify, render_template, request
from forms import (
    validar_dados_usuario,
    verificar_duplicidade,
    registrar_usuario,
    validar_login,
    autenticar_usuario,
)

# Criação do Blueprint único da aplicação
bp = Blueprint("main", __name__)


@bp.route("/")
def selecionar_perfil():
    """Tela inicial 'Quem é você?' (entrar ou criar conta)."""
    return render_template("perfil.html")


@bp.route("/cadastro/cliente")
def cadastro_cliente():
    """Formulário de cadastro do cliente."""
    return render_template("index.html")


@bp.route("/login/cliente")
def login_cliente():
    """Formulário de login do cliente."""
    return render_template("login_cliente.html")


@bp.route("/cadastro/tatuador")
def cadastro_tatuador():
    """Tela de cadastro do tatuador (ainda não implementada)."""
    return render_template("em_construcao.html", titulo="Criar conta — Tatuador")


@bp.route("/login/tatuador")
def login_tatuador():
    """Tela de login do tatuador (ainda não implementada)."""
    return render_template("em_construcao.html", titulo="Login — Tatuador")


@bp.route("/agendar")
def agendar_sessao():
    """Tela de agendamento de sessão do cliente.

    Front-end apenas por enquanto: calendário e horários são simulados
    em JS (static/js/agendar.js) até existir a tabela de agendamentos
    no Supabase. Também não há checagem de login ainda — qualquer
    pessoa consegue acessar essa URL diretamente por enquanto.
    """
    return render_template("agendar.html")


@bp.route("/anamnese")
def ficha_anamnese():
    """Ficha de anamnese (ainda não implementada)."""
    return render_template("em_construcao.html", titulo="Ficha de Anamnese")


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


@bp.route("/api/login/cliente", methods=["POST"])
def api_login_cliente():
    """Recebe e-mail e senha, valida e autentica o cliente no Supabase Auth."""
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    # --- 1. Validação de dados ---
    errors = validar_login(email, senha)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # --- 2. Autenticação no Supabase Auth ---
    try:
        user = autenticar_usuario(email, senha)
    except Exception as exc:
        error_msg = str(exc)
        if "Invalid login credentials" in error_msg:
            return jsonify({"success": False, "errors": {"geral": "E-mail ou senha incorretos."}}), 401

        return jsonify({"success": False, "errors": {"geral": error_msg}}), 500

    return jsonify({"success": True, "usuario": {"email": user.email}}), 200

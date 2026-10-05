from flask import Blueprint, jsonify, render_template, request
from forms import (
    validar_dados_usuario,
    verificar_duplicidade,
    registrar_usuario,
    validar_login,
    autenticar_usuario,
)
from db import supabase

# Criação do Blueprint único da aplicação
bp = Blueprint("main", __name__)


# ==========================================
# ROTAS DE PÁGINAS (TEMPLATES)
# ==========================================

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
    """Tela de agendamento de sessão do cliente."""
    return render_template("agendar.html")


@bp.route("/anamnese")
def ficha_anamnese():
    """Ficha de anamnese (ainda não implementada)."""
    return render_template("em_construcao.html", titulo="Ficha de Anamnese")

@bp.route("/dashboard")
def dashboard():
    """Área principal do cliente após efetuar o login."""
    return render_template("dashboard.html")


# ==========================================
# ROTAS DA API - AUTENTICAÇÃO
# ==========================================

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


# ==========================================
# ROTAS DA API - SERVIÇOS
# ==========================================

@bp.route("/api/servicos", methods=["GET"])
def listar_servicos():
    """Retorna a lista de serviços cadastrados no banco Supabase."""
    try:
        resposta = supabase.table("servicos").select("*").execute()
        return jsonify({"success": True, "servicos": resposta.data}), 200
    except Exception as exc:
        return jsonify({"success": False, "errors": {"geral": str(exc)}}), 500


# ==========================================
# ROTAS DA API - AGENDAMENTOS
# ==========================================

@bp.route("/api/agendamentos", methods=["POST"])
def criar_agendamento():
    """Recebe dados de agendamento e insere na tabela 'agendamentos' do Supabase."""
    data = request.get_json(silent=True) or {}

    cliente_id = data.get("cliente_id")
    servico_id = data.get("servico_id")
    data_hora = data.get("data_hora")
    observacoes = data.get("observacoes", "")

    if not all([cliente_id, servico_id, data_hora]):
        return jsonify({
            "success": False,
            "errors": {"geral": "Campos obrigatórios ausentes: cliente_id, servico_id e data_hora."}
        }), 400

    try:
        resposta = supabase.table("agendamentos").insert({
            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "data_hora": data_hora,
            "observacoes": observacoes,
            "status": "agendado"
        }).execute()

        return jsonify({
            "success": True,
            "mensagem": "Agendamento realizado com sucesso!",
            "agendamento": resposta.data
        }), 201
    except Exception as exc:
        return jsonify({"success": False, "errors": {"geral": str(exc)}}), 500


@bp.route("/api/agendamentos/cliente/<cliente_id>", methods=["GET"])
def listar_agendamentos_cliente(cliente_id):
    """Busca os agendamentos realizados por um cliente específico."""
    try:
        resposta = (
            supabase.table("agendamentos")
            .select("*, servicos(*)")
            .eq("cliente_id", cliente_id)
            .execute()
        )
        return jsonify({"success": True, "agendamentos": resposta.data}), 200
    except Exception as exc:
        return jsonify({"success": False, "errors": {"geral": str(exc)}}), 500


@bp.route("/api/agendamentos/<agendamento_id>/cancelar", methods=["PATCH"])
def cancelar_agendamento(agendamento_id):
    """Atualiza o status de um agendamento para 'cancelado'."""
    try:
        resposta = (
            supabase.table("agendamentos")
            .update({"status": "cancelado"})
            .eq("id", agendamento_id)
            .execute()
        )
        return jsonify({
            "success": True,
            "mensagem": "Agendamento cancelado com sucesso.",
            "agendamento": resposta.data
        }), 200
    except Exception as exc:
        return jsonify({"success": False, "errors": {"geral": str(exc)}}), 500
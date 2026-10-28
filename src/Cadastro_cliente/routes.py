from flask import Blueprint, jsonify, render_template, request
from forms import (
    validar_dados_usuario,
    verificar_duplicidade,
    registrar_usuario,
)

# Criação do Blueprint
bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Renders the HTML form page."""
    return render_template("index.html")


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

    # --- 3 & 4. Registro no Auth e Salvamento na tabela ---
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
from login_cliente.db import supabase


def validar_dados_usuario(nome, email, telefone, cpf, senha, confirmar):
    """Valida os campos do formulário e retorna um dicionário de erros, se houver."""
    errors = {}

    if len([p for p in nome.split(" ") if p]) < 2:
        errors["nome"] = "Informe seu nome completo."

    cpf_digits = "".join(ch for ch in cpf if ch.isdigit())
    if len(cpf_digits) != 11:
        errors["cpf"] = "Informe um CPF válido (11 dígitos)."

    if "@" not in email or "." not in email.split("@")[-1]:
        errors["email"] = "Informe um e-mail válido."

    tel_digits = "".join(ch for ch in telefone if ch.isdigit())
    if len(tel_digits) < 10:
        errors["telefone"] = "Informe um telefone válido (com DDD)."

    if len(senha) < 8:
        errors["senha"] = "A senha precisa ter no mínimo 8 caracteres."

    if senha != confirmar:
        errors["confirmar"] = "As senhas não coincidem."

    return errors, cpf_digits, tel_digits


def verificar_duplicidade(email, cpf_digits):
    """Verifica se o e-mail ou CPF já existem na tabela 'cliente'."""
    existente = (
        supabase.table("cliente")
        .select("email, cpf")
        .or_(f"email.eq.{email},cpf.eq.{cpf_digits}")
        .execute()
    )
    
    errors = {}
    if existente.data:
        for item in existente.data:
            if item.get("email") == email:
                errors["email"] = "Este e-mail já está cadastrado."
            if item.get("cpf") == cpf_digits:
                errors["cpf"] = "Este CPF já está cadastrado."
    return errors


def registrar_usuario(email, senha, nome, cpf_digits, tel_digits):
    """Realiza o cadastro no Supabase Auth e insere o perfil na tabela 'cliente'."""
    auth_response = supabase.auth.sign_up({
        "email": email,
        "password": senha,
    })

    user = auth_response.user
    if not user:
        raise Exception("Não foi possível criar a conta no sistema de autenticação.")

    supabase.table("cliente").insert({
        "auth_id": user.id,  
        "nome": nome,
        "email": email,
        "cpf": cpf_digits,
        "telefone": tel_digits,
    }).execute()

    return user


def autenticar_cliente(email, senha):
    """Entra no Supabase Auth e confirma que a conta pertence a um cliente.

    Retorna (dados_cliente, erro). Se deu certo, erro é None; se não, dados_cliente é None.
    """
    if not email or not senha:
        return None, "Informe e-mail e senha."

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })
    except Exception as exc:
        if "Email not confirmed" in str(exc):
            return None, "Confirme seu e-mail antes de entrar."
        return None, "E-mail ou senha incorretos."

    user = auth_response.user
    if not user:
        return None, "E-mail ou senha incorretos."

    # A conta existe no Auth, mas precisa ser de cliente (e não, por exemplo, de tatuador).
    perfil = (
        supabase.table("cliente")
        .select("nome, email")
        .eq("auth_id", user.id)
        .limit(1)
        .execute()
    )
    if not perfil.data:
        supabase.auth.sign_out()
        return None, "Esta conta não é de cliente. Entre pela área do tatuador."

    return {"id": user.id, "nome": perfil.data[0]["nome"], "email": email}, None

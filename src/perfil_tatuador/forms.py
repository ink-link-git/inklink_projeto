from login_tatuador.db import supabase
from shared.utils import parse_data_hora

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MAX_NOME = 100


def iniciais(nome):
    """'Milena Guido' -> 'MG'"""
    partes = (nome or "").split()
    return ((partes[0][:1] if partes else "?") + (partes[1][:1] if len(partes) > 1 else "")).upper()


def formatar_telefone(valor):
    digitos = "".join(ch for ch in str(valor or "") if ch.isdigit())
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return digitos


def membro_desde(registro):
    for chave in ("created_at", "criado_em", "data_cadastro"):
        dt = parse_data_hora(registro.get(chave))
        if dt:
            return f"{MESES[dt.month - 1]} {dt.year}"
    return None


def buscar_perfil(tatuador_id):
    """Busca o perfil na tabela 'tatuador' filtrando pela coluna correta 'id_tatuador'."""
    resposta = supabase.table("tatuador").select("*").eq("id_tatuador", tatuador_id).limit(1).execute()
    if not resposta.data:
        return None

    tatuador = resposta.data[0]
    nome = (tatuador.get("nome") or "").strip()
    return {
        "nome": nome,
        "email": (tatuador.get("email") or "").strip(),
        "telefone": formatar_telefone(tatuador.get("tel")),
        "endereco": tatuador.get("endereco") or "",        # <-- Adicionado
        "avatar_url": tatuador.get("avatar_url") or "",    # <-- Adicionado
        "iniciais": iniciais(nome),
        "desde": membro_desde(tatuador),
    }


def estatisticas(tatuador_id):
    """Estatísticas do tatuador usando 'id_tatuador' na tabela de agendamentos."""
    resposta = (
        supabase.table("agendamento")
        .select("status, cliente_auth_id")
        .eq("id_tatuador", tatuador_id)
        .execute()
    )

    realizados, clientes, pendentes = 0, set(), 0
    for item in resposta.data or []:
        status = (item.get("status") or "PENDENTE").upper()
        if status == "REALIZADO":
            realizados += 1
            if item.get("cliente_auth_id"):
                clientes.add(item.get("cliente_auth_id"))
        elif status == "PENDENTE":
            pendentes += 1

    return {"realizados": realizados, "clientes": len(clientes), "pendentes": pendentes}


def validar_perfil(nome, telefone):
    errors = {}

    if len([p for p in nome.split(" ") if p]) < 2:
        errors["nome"] = "Informe seu nome completo."
    elif len(nome) > MAX_NOME:
        errors["nome"] = f"O nome pode ter no máximo {MAX_NOME} caracteres."

    tel_digits = "".join(ch for ch in telefone if ch.isdigit())
    if len(tel_digits) < 10 or len(tel_digits) > 11:
        errors["telefone"] = "Informe um telefone válido (com DDD)."

    return errors, tel_digits


def atualizar_perfil(tatuador_id, nome, tel_digits, endereco="", avatar_url=None):
    """Atualiza nome, telefone, endereço e avatar do tatuador no banco."""
    dados_para_atualizar = {
        "nome": nome, 
        "tel": tel_digits,
        "endereco": endereco
    }
    
    if avatar_url:
        dados_para_atualizar["avatar_url"] = avatar_url

    resposta = (
        supabase.table("tatuador")
        .update(dados_para_atualizar)
        .eq("id_tatuador", tatuador_id)
        .execute()
    )
    if not resposta.data:
        raise Exception("Nenhum registro de tatuador foi atualizado.")
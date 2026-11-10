from login_cliente.db import supabase
from shared.utils import parse_data_hora

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MAX_NOME = 100


def iniciais(nome):
    """'Lucas Mendes' -> 'LM' (mesmas iniciais do avatar da barra lateral)."""
    partes = (nome or "").split()
    return ((partes[0][:1] if partes else "?") + (partes[1][:1] if len(partes) > 1 else "")).upper()


def formatar_telefone(valor):
    """'12999999999' -> '(12) 99999-9999'. Se não tiver 10 ou 11 dígitos, devolve só os dígitos."""
    digitos = "".join(ch for ch in str(valor or "") if ch.isdigit())
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return digitos


def membro_desde(registro):
    """'Ago 2026', a partir da data de criação do cliente (ou None se a tabela não tiver essa coluna)."""
    for chave in ("created_at", "criado_em", "data_cadastro"):
        dt = parse_data_hora(registro.get(chave))
        if dt:
            return f"{MESES[dt.month - 1]} {dt.year}"
    return None


def buscar_perfil(auth_id):
    """Dados do cliente logado (ou None se não houver registro dele na tabela 'cliente')."""
    resposta = supabase.table("cliente").select("*").eq("auth_id", auth_id).limit(1).execute()
    if not resposta.data:
        return None

    cliente = resposta.data[0]
    nome = (cliente.get("nome") or "").strip()
    return {
        "nome": nome,
        "email": (cliente.get("email") or "").strip(),
        "telefone": formatar_telefone(cliente.get("telefone")),
        "iniciais": iniciais(nome),
        "desde": membro_desde(cliente),
    }


def estatisticas(auth_id):
    """Números do resumo: tatuagens feitas, artistas diferentes e pedidos pendentes."""
    resposta = (
        supabase.table("agendamento")
        .select("status, id_tatuador")
        .eq("cliente_auth_id", auth_id)
        .execute()
    )

    tatuagens, artistas, pendentes = 0, set(), 0
    for item in resposta.data or []:
        status = (item.get("status") or "PENDENTE").upper()
        if status == "REALIZADO":
            tatuagens += 1
            artistas.add(item.get("id_tatuador"))
        elif status == "PENDENTE":
            pendentes += 1

    return {"tatuagens": tatuagens, "artistas": len(artistas), "pendentes": pendentes}


def validar_perfil(nome, telefone):
    """Mesmas regras do cadastro. Retorna (errors, tel_digits)."""
    errors = {}

    if len([p for p in nome.split(" ") if p]) < 2:
        errors["nome"] = "Informe seu nome completo."
    elif len(nome) > MAX_NOME:
        errors["nome"] = f"O nome pode ter no máximo {MAX_NOME} caracteres."

    tel_digits = "".join(ch for ch in telefone if ch.isdigit())
    if len(tel_digits) < 10 or len(tel_digits) > 11:
        errors["telefone"] = "Informe um telefone válido (com DDD)."

    return errors, tel_digits


def atualizar_perfil(auth_id, nome, tel_digits):
    """Grava nome e telefone do cliente. O e-mail não muda aqui (é o login da conta)."""
    resposta = (
        supabase.table("cliente")
        .update({"nome": nome, "telefone": tel_digits})
        .eq("auth_id", auth_id)
        .execute()
    )
    if not resposta.data:
        # O Supabase devolve lista vazia quando nenhuma linha foi alterada
        # (cliente não encontrado ou sem permissão de UPDATE na tabela).
        raise Exception("Nenhum registro de cliente foi atualizado (confira a política de UPDATE da tabela 'cliente').")

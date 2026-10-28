from datetime import datetime

# Preferência de período que o cliente pode indicar (o tatuador decide a hora exata).
PERIODOS = {"manha": "Manhã", "tarde": "Tarde", "noite": "Noite", "qualquer": "Sem preferência"}

DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def parse_data_hora(valor):
    """Converte o texto vindo do Supabase/formulário em datetime (ou None)."""
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "").split("+")[0])
    except ValueError:
        return None


def formatar_data_hora(valor):
    """Filtro Jinja: '2026-11-02T09:00:00' -> 'seg, 02/11/2026 às 09:00'."""
    dt = parse_data_hora(valor)
    if not dt:
        return valor or ""
    return f"{DIAS[dt.weekday()]}, {dt:%d/%m/%Y} às {dt:%H:%M}"


def inicial(nome):
    """Primeira letra do nome, para o avatar."""
    return (nome or "?").strip()[:1].upper()


def formatar_dia(valor):
    """Filtro Jinja: '2026-11-02' (ou data/hora) -> 'seg, 02/11/2026'."""
    dt = parse_data_hora(valor)
    if not dt:
        return valor or ""
    return f"{DIAS[dt.weekday()]}, {dt:%d/%m/%Y}"


def quando(item):
    """Filtro Jinja: horário marcado, ou o dia pedido + período enquanto ainda não foi confirmado."""
    if item.get("data_hora"):
        return formatar_data_hora(item["data_hora"])
    texto = formatar_dia(item.get("data_desejada"))
    periodo = PERIODOS.get(item.get("periodo"))
    if periodo and item.get("periodo") != "qualquer":
        texto += f" · prefere {periodo.lower()}"
    return texto + " (horário a definir)"

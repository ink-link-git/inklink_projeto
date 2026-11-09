import os

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def trocar_senha(email, senha_atual, nova_senha):
    """Confere a senha atual e grava a nova no Supabase Auth.

    Usa um cliente TEMPORÁRIO: entrar (sign_in) no cliente compartilhado do
    projeto trocaria a sessão dele e afetaria as outras telas.
    Retorna (ok, erro) — erro é "senha_atual" quando a senha atual está errada.
    """
    cliente = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        cliente.auth.sign_in_with_password({"email": email, "password": senha_atual})
    except Exception:
        return False, "senha_atual"

    cliente.auth.update_user({"password": nova_senha})
    try:
        cliente.auth.sign_out()
    except Exception:
        pass
    return True, None

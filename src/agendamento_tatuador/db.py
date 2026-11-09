import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Se existir uma chave de serviço no .env ela é usada (só no servidor, nunca no navegador).
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
    or os.getenv("SUPABASE_KEY")
)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Verifique o arquivo .env: SUPABASE_URL ou SUPABASE_KEY não foram encontrados.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

import os
from dotenv import load_dotenv
from supabase import Client, create_client

# Força o recarregamento das variáveis do .env
load_dotenv(override=True)

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip()

print(f"[DEBUG] URL carregada: {SUPABASE_URL}")
print(f"[DEBUG] Tamanho da KEY carregada: {len(SUPABASE_KEY)} caracteres")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY ausentes ou vazias no arquivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
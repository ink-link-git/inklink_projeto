import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Força o carregamento do arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Verifica se as chaves foram carregadas antes de conectar
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Verifique o arquivo .env: SUPABASE_URL ou SUPABASE_ANON_KEY não foram encontrados.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
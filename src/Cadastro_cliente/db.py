import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

# Busque pelo NOME da variável declarada no .env
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY no arquivo .env.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
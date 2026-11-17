import os
from supabase import create_client, Client

<<<<<<< HEAD

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
=======
# Substitua pelas suas chaves ou use variáveis no arquivo .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
>>>>>>> cb74ef9b567c27a6726450cfd805c41947aac95e
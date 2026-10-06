import os
from supabase import create_client, Client

# Substitua pelas suas chaves ou use variáveis no arquivo .env
SUPABASE_URL = "https://vhopdstyxrpzlhgfmqnu.supabase.co"
SUPABASE_KEY = "sb_publishable_PJ0xKOMvOBwypfvOgYAvfg_JHJA7gvL"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
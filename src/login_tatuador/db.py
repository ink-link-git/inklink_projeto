#Biblioteca nativa do Python para lidar com S.O, nesse caso usada para ler as variáveis do ambiente (.env)
import os
# importa a função que cria a conexao com o o Supabase e Client tipo de dado para dar dica de tipo  
from supabase import create_client, Client
#Carrega as variaveis do arquivo env.
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

#buscar valores do .env
SUPABASE_URL= os.getenv("SUPABASE_URL")
SUPABASE_KEY= os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Verifique o arquivo .env: SUPABASE_URL ou SUPABASE_ANON_KEY não foram encontrados.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

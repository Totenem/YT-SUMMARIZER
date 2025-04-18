from config import GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
user_id = "b1334885-5510-4897-a0fa-a38df2cc7e96"

# Fetch user profile
response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
print(response)
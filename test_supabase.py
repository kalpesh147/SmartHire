# test_supabase.py
from database.supabase_client import supabase

def test_connection():
    try:
        response = supabase.table("Resumes").select("*").limit(1).execute()
        print("✅ Supabase is working! Sample data:", response.data)
    except Exception as e:
        print("❌ Error connecting to Supabase:", e)

test_connection()


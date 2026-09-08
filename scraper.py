import os
import urllib.parse
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wimjkvkprixuumnuabjd.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

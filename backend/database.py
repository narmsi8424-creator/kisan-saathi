import httpx
from config import settings

async def init_db():
    print("✅ Database connected!")

def _headers(use_service_key: bool = False) -> dict:
    key = settings.SUPABASE_SERVICE_KEY if use_service_key else settings.SUPABASE_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
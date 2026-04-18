import httpx
from datetime import datetime
from config import settings

def _headers(service=False):
    key = settings.SUPABASE_SERVICE_KEY if service else settings.SUPABASE_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

async def get_or_create_farmer(phone, name):
    farmer = await _get_farmer(phone)
    if farmer:
        return farmer
    return await _create_farmer(phone, name)

async def _get_farmer(phone):
    url = f"{settings.SUPABASE_URL}/rest/v1/farmers"
    params = {"phone": f"eq.{phone}", "limit": "1"}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=_headers(), params=params)
        data = resp.json()
    return data[0] if data else None

async def _create_farmer(phone, name):
    url = f"{settings.SUPABASE_URL}/rest/v1/farmers"
    payload = {
        "phone": phone,
        "name": name,
        "language": "hi",
        "state": "Bihar",
        "created_at": datetime.utcnow().isoformat(),
        "plan": "free",
        "message_count": 0,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, headers=_headers(service=True), json=payload)
        data = resp.json()
    return data[0] if isinstance(data, list) else payload
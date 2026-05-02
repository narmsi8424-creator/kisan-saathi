import httpx
from config import settings

SUPABASE_URL = settings.SUPABASE_URL
HEADERS = {
    "apikey": settings.SUPABASE_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    "Content-Type": "application/json",
}

async def get_or_create_farmer(phone: str, name: str = "Kisan Bhai") -> dict:
    async with httpx.AsyncClient(timeout=10) as client:

        # Pehle check karo farmer exist karta hai ya nahi
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers=HEADERS,
            params={"phone_number": f"eq.{phone}", "select": "*"},
        )

        if response.status_code == 200 and response.json():
            farmer = response.json()[0]
            return {
                "phone": farmer.get("phone_number", phone),
                "name": farmer.get("name", name),
                "language": farmer.get("language", "Hindi"),
                "state": farmer.get("state", "Bihar"),
                "district": farmer.get("district", "Patna"),
                "plan": farmer.get("plan", "free"),
            }

        # Farmer nahi mila — naya banao
        new_farmer = {
            "phone_number": phone,
            "name": name,
            "language": "Hindi",
            "state": "Jharkhand",
            "district": "Chatra",
            "plan": "free",
        }

        await client.post(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers=HEADERS,
            json=new_farmer,
        )

        return {
            "phone": phone,
            "name": name,
            "language": "Hindi",
            "state": "Jharkhand",
            "district": "Chatra",
            "plan": "free",
        }


async def update_farmer_language(phone: str, language: str):
    async with httpx.AsyncClient(timeout=10) as client:
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers={**HEADERS, "Prefer": "return=minimal"},
            params={"phone_number": f"eq.{phone}"},
            json={"language": language},
        )
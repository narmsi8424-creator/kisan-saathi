import httpx
from config import settings

SUPABASE_URL = settings.SUPABASE_URL
HEADERS = {
    "apikey": settings.SUPABASE_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
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
            print(f"FARMER FOUND: {phone}")
            return {
                "phone": farmer.get("phone_number", phone),
                "name": farmer.get("name", name),
                "language": farmer.get("language", "Hindi"),
                "state": farmer.get("state", "Jharkhand"),
                "district": farmer.get("district", "Chatra"),
                "plan": farmer.get("plan", "free"),
            }

        # Farmer nahi mila — naya banao
        print(f"FARMER NOT FOUND — creating new: {phone}")
        new_farmer = {
            "phone_number": phone,
            "name": name,
            "language": "Hindi",
            "state": "Jharkhand",
            "district": "Chatra",
            "plan": "free",
        }

        insert_response = await client.post(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers=HEADERS,
            json=new_farmer,
        )

        print(f"FARMER SAVE STATUS: {insert_response.status_code}")
        print(f"FARMER SAVE BODY: {insert_response.text}")

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
        resp = await client.patch(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers={**HEADERS, "Prefer": "return=minimal"},
            params={"phone_number": f"eq.{phone}"},
            json={"language": language},
        )
        print(f"LANGUAGE UPDATE: {phone} → {language} ({resp.status_code})")
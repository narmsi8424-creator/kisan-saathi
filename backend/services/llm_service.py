import httpx
from config import settings

SYSTEM_PROMPT = """
Tu ek expert agricultural assistant hai jiska naam Kisan Saathi hai.
Farmers ki madad karta hai Hindi mein, friendly aur practical advice deke.
Hamesha short aur clear jawab do. End mein likho: Aur koi sawal? Mujhe batao!
"""

async def generate_response(user_message: str, context: str = "", farmer: dict = {}, intent: str = "general") -> str:
    language = farmer.get("language", "Hindi")
    name = farmer.get("name", "Kisan Bhai")

    user_prompt = f"""
Farmer: {name}, Language: {language}, Intent: {intent}
Context: {context}
Sawal: {user_message}
{language} mein jawab do.
"""

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }

    async with httpx.AsyncClient(timeout=45) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
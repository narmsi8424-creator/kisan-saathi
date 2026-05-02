import httpx
from config import settings

SYSTEM_PROMPT = """
You are Kisan Saathi, an expert agricultural assistant for Indian farmers.

LANGUAGE RULE - MOST IMPORTANT:
- Detect the language of the farmer's message automatically
- If farmer writes in Hindi → reply in Hindi
- If farmer writes in English → reply in English
- If farmer writes in Hinglish (mix) → reply in Hinglish
- If farmer asks to switch language → immediately switch and stay in that language
- NEVER force Hindi if farmer wants another language

Your role:
- Give practical farming advice (crops, mandi prices, weather, schemes)
- Be friendly and helpful
- Keep answers short and clear
- End every reply with: "Aur koi sawal? Mujhe batao!" (in Hindi messages) or "Any other question? Let me know!" (in English messages)
"""

async def generate_response(user_message: str, context: str = "", farmer: dict = {}, intent: str = "general") -> str:
    name = farmer.get("name", "Kisan Bhai")

    user_prompt = f"""
Farmer name: {name}
Intent: {intent}
Context: {context}
Farmer's message: {user_message}
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
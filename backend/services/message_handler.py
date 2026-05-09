from services.llm_service import generate_response
from services.mandi_service import get_mandi_prices
from services.weather_service import get_weather
from services.rag_service import retrieve_context
from services.vision_service import analyze_plant_image
import httpx
from config import settings

async def handle_message(farmer, msg_type, content, chat_history=[]):
    text = content.get("text", "")
    intent = detect_intent(text)
    context = ""

    if msg_type == "image":
        image_id = content.get("image_id", "")
        image_bytes = await download_image(image_id)
        reply = await analyze_plant_image(image_data=image_bytes)
        return reply, "text"

    if intent == "mandi_price":
        crop = extract_crop(text)
        context = await get_mandi_prices(crop, farmer.get("state", "Jharkhand"))

    elif intent == "weather":
        context = await get_weather(
            farmer.get("district", "Chatra"),
            farmer.get("state", "Jharkhand")
        )
        if not context or len(context) < 20:
            context = (
                f"{farmer.get('district', 'Chatra')}, "
                f"{farmer.get('state', 'Jharkhand')} ka mausam: "
                f"Abhi API se data aa raha hai. "
                f"Saamanya tor par is mausam mein apni fasal ka dhyan rakhein."
            )

    elif intent == "govt_scheme":
        context = await retrieve_context(text)

    elif intent == "disease_query":
        context = await retrieve_context(text)

    elif intent == "general_agri":
        crop = extract_crop(text)
        if crop != "general":
            context = await retrieve_context(text)

    reply = await generate_response(
        user_message=text,
        context=context,
        farmer=farmer,
        intent=intent,
        chat_history=chat_history,
    )
    return reply, "text"


async def download_image(image_id: str) -> bytes:
    url = f"https://graph.facebook.com/v18.0/{image_id}"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=headers)
        image_url = resp.json()["url"]
        img_resp = await client.get(image_url, headers=headers)
        return img_resp.content


def detect_intent(text):
    text_lower = text.lower()

    if any(k in text_lower for k in [
        "bhav", "rate", "mandi", "bechna", "daam", "price",
        "bikri", "sell", "bazar", "market"
    ]):
        return "mandi_price"

    if any(k in text_lower for k in [
        "mausam", "barish", "weather", "rain", "baarish",
        "tufan", "aandhi", "garmi", "sardi", "temperature",
        "forecast", "kal ka mausam", "aaj ka mausam", "barsaat"
    ]):
        return "weather"

    if any(k in text_lower for k in [
        "yojana", "scheme", "subsidy", "pm kisan", "pm-kisan",
        "bima", "loan", "kcc", "register", "paisa", "sarkar",
        "government", "apply", "fasal bima", "kisan credit",
        "msp", "support price", "helpline", "documents"
    ]):
        return "govt_scheme"

    if any(k in text_lower for k in [
        "bimari", "disease", "keeda", "pest", "dhabbe", "peela",
        "patta", "leaves", "yellow", "kharab", "rot", "fungus",
        "spray", "dawai", "medicine", "insect", "bug", "worm",
        "neem", "infection"
    ]):
        return "disease_query"

    return "general_agri"


def extract_crop(text):
    text_lower = text.lower()

    # Exact mapping — wheat aur sugarcane alag hain!
    crop_map = {
        "wheat": "wheat",
        "gehu": "wheat",
        "gehun": "wheat",
        "gahu": "wheat",
        "rice": "rice",
        "dhan": "rice",
        "paddy": "rice",
        "chawal": "rice",
        "mustard": "mustard",
        "sarson": "mustard",
        "potato": "potato",
        "aloo": "potato",
        "onion": "onion",
        "pyaz": "onion",
        "maize": "maize",
        "makka": "maize",
        "corn": "maize",
        "bhutta": "maize",
        "tomato": "tomato",
        "tamatar": "tomato",
        "sugarcane": "sugarcane",   # ← wheat se bilkul alag
        "ganna": "sugarcane",
        "ikh": "sugarcane",
        "soybean": "soybean",
        "soya": "soybean",
        "cotton": "cotton",
        "kapas": "cotton",
        "gram": "gram",
        "chana": "gram",
    }

    for keyword, crop_name in crop_map.items():
        if keyword in text_lower:
            print(f"CROP DETECTED: '{keyword}' → {crop_name}")
            return crop_name

    return "general"
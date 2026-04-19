from services.llm_service import generate_response
from services.mandi_service import get_mandi_prices
from services.weather_service import get_weather
from services.rag_service import retrieve_context
from services.vision_service import analyze_plant_image
import httpx
from config import settings

async def handle_message(farmer, msg_type, content):
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
        context = await get_mandi_prices(crop, farmer.get("state", "Bihar"))
    elif intent == "weather":
        context = await get_weather(
            farmer.get("district", "Patna"),
            farmer.get("state", "Bihar")
        )
    elif intent == "govt_scheme":
        context = await retrieve_context(text)
    elif intent == "disease_query":
        context = await retrieve_context(text)

    reply = await generate_response(
        user_message=text,
        context=context,
        farmer=farmer,
        intent=intent,
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
    text = text.lower()
    if any(k in text for k in ["bhav","rate","mandi","bechna","daam","price"]):
        return "mandi_price"
    if any(k in text for k in ["mausam","barish","weather","rain","baarish"]):
        return "weather"
    if any(k in text for k in ["yojana","scheme","subsidy","pm kisan","pm-kisan","bima","loan","kcc"]):
        return "govt_scheme"
    if any(k in text for k in ["bimari","disease","keeda","pest","dhabbe","peela"]):
        return "disease_query"
    return "general_agri"

def extract_crop(text):
    crops = ["wheat","gehu","rice","dhan","mustard","sarson",
             "potato","aloo","onion","pyaz","maize","makka","tomato","tamatar"]
    for crop in crops:
        if crop in text.lower():
            return crop
    return "wheat"
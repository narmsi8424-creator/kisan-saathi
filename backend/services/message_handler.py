from services.llm_service import generate_response
from services.mandi_service import get_mandi_prices
from services.weather_service import get_weather_advisory

async def handle_message(farmer, msg_type, content):
    text = content.get("text", "")
    intent = detect_intent(text)
    context = ""

    if intent == "mandi_price":
        crop = extract_crop(text)
        context = await get_mandi_prices(crop, farmer.get("state", "Bihar"))
    elif intent == "weather":
        context = await get_weather_advisory(
            farmer.get("district", "Patna"),
            farmer.get("state", "Bihar")
        )

    reply = await generate_response(
        user_message=text,
        context=context,
        farmer=farmer,
        intent=intent,
    )
    return reply, "text"

def detect_intent(text):
    text = text.lower()
    if any(k in text for k in ["bhav","rate","mandi","bechna","daam"]):
        return "mandi_price"
    if any(k in text for k in ["mausam","barish","weather","rain"]):
        return "weather"
    if any(k in text for k in ["yojana","scheme","subsidy","pm kisan"]):
        return "govt_scheme"
    if any(k in text for k in ["bimari","disease","keeda","pest"]):
        return "disease_query"
    return "general_agri"

def extract_crop(text):
    crops = ["wheat","gehu","rice","dhan","mustard","sarson",
             "potato","aloo","onion","pyaz","maize","makka"]
    for crop in crops:
        if crop in text.lower():
            return crop
    return "wheat"
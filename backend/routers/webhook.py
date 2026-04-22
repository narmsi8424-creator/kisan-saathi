from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
import httpx
from config import settings
from services.message_handler import handle_message
from services.farmer_service import get_or_create_farmer
from services.bhashini_service import speech_to_text

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if (params.get("hub.mode") == "subscribe" and
            params.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN):
        return PlainTextResponse(params.get("hub.challenge"))
    return PlainTextResponse("Error", status_code=403)

@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    try:
        msg = body["entry"][0]["changes"][0]["value"]
        if "messages" not in msg:
            return {"status": "ok"}
        message = msg["messages"][0]
        contact = msg["contacts"][0]
        phone = message["from"]
        name = contact["profile"]["name"]
        msg_type = message["type"]
        content = {}
        if msg_type == "text":
            content = {"text": message["text"]["body"]}
        elif msg_type == "audio":
            audio_id = message["audio"]["id"]
            audio_bytes = await download_media(audio_id)
            text = await speech_to_text(audio_bytes)
            content = {"text": text or "Voice message samajh nahi aaya"}
            msg_type = "text"
        elif msg_type == "image":
            image_id = message["image"]["id"]
            content = {"image_id": image_id}
        background_tasks.add_task(process_reply, phone, name, msg_type, content)
        return {"status": "received"}
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}")
        return {"status": "ignored"}

async def download_media(media_id: str) -> bytes:
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        media_url = resp.json()["url"]
        media_resp = await client.get(media_url, headers=headers)
        return media_resp.content

async def process_reply(phone, name, msg_type, content):
    try:
        print(f"PROCESSING: {phone} {msg_type}")
        farmer = await get_or_create_farmer(phone, name)
        reply, _ = await handle_message(farmer, msg_type, content)
        print(f"REPLY GENERATED: {reply[:50]}")
        await send_reply(phone, reply)
    except Exception as e:
        print(f"PROCESS ERROR: {e}")

async def send_reply(phone, text):
    url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=headers, json=payload)
        print(f"REPLY STATUS: {resp.status_code}")
        print(f"REPLY BODY: {resp.text}")
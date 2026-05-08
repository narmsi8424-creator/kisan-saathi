from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
import httpx
import time
from config import settings
from services.message_handler import handle_message
from services.farmer_service import get_or_create_farmer
from services.bhashini_service import speech_to_text

router = APIRouter()

# ── RATE LIMITING (5 messages per 60 seconds per number) ──────
RATE_LIMIT = {}
MAX_MESSAGES = 5
TIME_WINDOW = 60

def is_rate_limited(phone: str) -> bool:
    now = time.time()
    if phone not in RATE_LIMIT:
        RATE_LIMIT[phone] = []
    RATE_LIMIT[phone] = [t for t in RATE_LIMIT[phone] if now - t < TIME_WINDOW]
    if len(RATE_LIMIT[phone]) >= MAX_MESSAGES:
        print(f"RATE LIMITED: {phone}")
        return True
    RATE_LIMIT[phone].append(now)
    return False

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

        # Rate limit check
        if is_rate_limited(phone):
            return {"status": "rate_limited"}

        content = {}
        if msg_type == "text":
            text = message["text"]["body"]
            if len(text) > 1000:
                text = text[:1000]
            content = {"text": text}
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


# ── UPDATED: process_reply with history + feedback ─────────────
async def process_reply(phone, name, msg_type, content):
    try:
        print(f"PROCESSING: {phone} {msg_type}")

        # ── Farmer fetch ────────────────────────────────────────
        try:
            farmer = await get_or_create_farmer(phone, name)
            print(f"FARMER OK: {farmer}")
        except Exception as fe:
            print(f"FARMER ERROR: {fe}")
            farmer = {
                "phone": phone,
                "name": name,
                "language": "Hindi",
                "state": "Jharkhand",
                "district": "Chatra",
                "plan": "free",
            }

        # ── Feedback check ──────────────────────────────────────
        # Agar user ne "1" ya "2" bheja toh feedback handle karo
        if msg_type == "text":
            text = content.get("text", "").strip()
            if text in ["1", "2"]:
                await handle_feedback(phone, text)
                return

        # ── Chat History fetch ──────────────────────────────────
        chat_history = await get_chat_history(phone)
        print(f"HISTORY LOADED: {len(chat_history)} messages")

        # ── Main reply generate ─────────────────────────────────
        reply, _ = await handle_message(farmer, msg_type, content, chat_history=chat_history)
        print(f"REPLY GENERATED: {reply[:50]}")

        # ── Reply bhejo ─────────────────────────────────────────
        await send_reply(phone, reply)

        # ── Feedback message bhejo ──────────────────────────────
        feedback_msg = (
            "Kya yeh jawab helpful tha? 🙏\n"
            "*1* 👍 Haan, bahut acha\n"
            "*2* 👎 Nahi, aur help chahiye"
        )
        await send_reply(phone, feedback_msg)

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


# ── NEW: Chat History fetch karo Supabase se ───────────────────
async def get_chat_history(phone: str) -> list:
    try:
        from database import supabase
        result = supabase.table("messages") \
            .select("content, direction") \
            .eq("phone", phone) \
            .eq("msg_type", "text") \
            .order("created_at", desc=True) \
            .limit(6) \
            .execute()

        history = []
        for row in reversed(result.data):
            role = "user" if row["direction"] == "inbound" else "assistant"
            text = row.get("content", "")
            if text:
                history.append({"role": role, "content": text})

        return history
    except Exception as e:
        print(f"HISTORY FETCH ERROR: {e}")
        return []


# ── NEW: Feedback save karo Supabase mein ──────────────────────
async def handle_feedback(phone: str, feedback: str):
    try:
        from database import supabase
        flag = "positive" if feedback == "1" else "needs_review"

        # Last AI message dhundho
        result = supabase.table("messages") \
            .select("id") \
            .eq("phone", phone) \
            .eq("direction", "outbound") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()

        if result.data:
            msg_id = result.data[0]["id"]
            supabase.table("messages") \
                .update({"intent": flag}) \
                .eq("id", msg_id) \
                .execute()
            print(f"FEEDBACK SAVED: {phone} → {flag}")

        # Thank you message
        if feedback == "1":
            await send_reply(
                phone,
                "Shukriya ji! Aapka feedback hamare liye bahut important hai 🙏🌾"
            )
        else:
            await send_reply(
                phone,
                "Maafi ji! 🙏 Aap apna sawal dobara poochhein — main aur detail mein samjhaata hoon! 🌾"
            )
    except Exception as e:
        print(f"FEEDBACK ERROR: {e}")
import httpx
from config import settings

SUPABASE_URL = settings.SUPABASE_URL
HEADERS = {
    "apikey": settings.SUPABASE_KEY,
    "Authorization": f"Bearer {settings.SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── India ke major STD codes se state detect karo ─────────────
PHONE_STATE_MAP = {
    # Jharkhand
    "06521": ("Jharkhand", "Chatra"),
    "06522": ("Jharkhand", "Hazaribagh"),
    "0651":  ("Jharkhand", "Ranchi"),
    "0657":  ("Jharkhand", "Jamshedpur"),
    "06542": ("Jharkhand", "Dhanbad"),
    "06432": ("Jharkhand", "Dumka"),

    # Bihar
    "0612":  ("Bihar", "Patna"),
    "0621":  ("Bihar", "Muzaffarpur"),
    "06452": ("Bihar", "Gaya"),
    "0641":  ("Bihar", "Bhagalpur"),

    # UP
    "0522":  ("Uttar Pradesh", "Lucknow"),
    "0532":  ("Uttar Pradesh", "Prayagraj"),
    "0542":  ("Uttar Pradesh", "Varanasi"),
    "0581":  ("Uttar Pradesh", "Bareilly"),

    # MP
    "0755":  ("Madhya Pradesh", "Bhopal"),
    "0731":  ("Madhya Pradesh", "Indore"),
    "0751":  ("Madhya Pradesh", "Gwalior"),

    # Rajasthan
    "0141":  ("Rajasthan", "Jaipur"),
    "0291":  ("Rajasthan", "Jodhpur"),
    "0744":  ("Rajasthan", "Kota"),

    # Punjab
    "0161":  ("Punjab", "Ludhiana"),
    "0183":  ("Punjab", "Amritsar"),

    # Haryana
    "0124":  ("Haryana", "Gurugram"),
    "0171":  ("Haryana", "Ambala"),

    # Maharashtra
    "022":   ("Maharashtra", "Mumbai"),
    "020":   ("Maharashtra", "Pune"),
    "0712":  ("Maharashtra", "Nagpur"),

    # Gujarat
    "079":   ("Gujarat", "Ahmedabad"),
    "0265":  ("Gujarat", "Surat"),

    # West Bengal
    "033":   ("West Bengal", "Kolkata"),
    "0342":  ("West Bengal", "Asansol"),
}

# ── Message mein location keywords detect karo ─────────────────
LOCATION_KEYWORDS = {
    # Jharkhand districts
    "ranchi": ("Jharkhand", "Ranchi"),
    "jamshedpur": ("Jharkhand", "Jamshedpur"),
    "dhanbad": ("Jharkhand", "Dhanbad"),
    "hazaribagh": ("Jharkhand", "Hazaribagh"),
    "chatra": ("Jharkhand", "Chatra"),
    "dumka": ("Jharkhand", "Dumka"),
    "bokaro": ("Jharkhand", "Bokaro"),
    "giridih": ("Jharkhand", "Giridih"),
    "deoghar": ("Jharkhand", "Deoghar"),
    "palamu": ("Jharkhand", "Palamu"),
    "lohardaga": ("Jharkhand", "Lohardaga"),
    "gumla": ("Jharkhand", "Gumla"),
    "simdega": ("Jharkhand", "Simdega"),
    "ramgarh": ("Jharkhand", "Ramgarh"),
    "jharkhand": ("Jharkhand", "Ranchi"),

    # Bihar
    "patna": ("Bihar", "Patna"),
    "gaya": ("Bihar", "Gaya"),
    "muzaffarpur": ("Bihar", "Muzaffarpur"),
    "bhagalpur": ("Bihar", "Bhagalpur"),
    "bihar": ("Bihar", "Patna"),
    "nalanda": ("Bihar", "Nalanda"),
    "vaishali": ("Bihar", "Vaishali"),

    # UP
    "lucknow": ("Uttar Pradesh", "Lucknow"),
    "varanasi": ("Uttar Pradesh", "Varanasi"),
    "agra": ("Uttar Pradesh", "Agra"),
    "kanpur": ("Uttar Pradesh", "Kanpur"),
    "meerut": ("Uttar Pradesh", "Meerut"),
    "allahabad": ("Uttar Pradesh", "Prayagraj"),
    "prayagraj": ("Uttar Pradesh", "Prayagraj"),
    "gorakhpur": ("Uttar Pradesh", "Gorakhpur"),

    # MP
    "bhopal": ("Madhya Pradesh", "Bhopal"),
    "indore": ("Madhya Pradesh", "Indore"),
    "gwalior": ("Madhya Pradesh", "Gwalior"),
    "jabalpur": ("Madhya Pradesh", "Jabalpur"),

    # Rajasthan
    "jaipur": ("Rajasthan", "Jaipur"),
    "jodhpur": ("Rajasthan", "Jodhpur"),
    "udaipur": ("Rajasthan", "Udaipur"),
    "kota": ("Rajasthan", "Kota"),

    # Punjab/Haryana
    "ludhiana": ("Punjab", "Ludhiana"),
    "amritsar": ("Punjab", "Amritsar"),
    "chandigarh": ("Punjab", "Chandigarh"),
    "ambala": ("Haryana", "Ambala"),
    "hisar": ("Haryana", "Hisar"),

    # Maharashtra
    "mumbai": ("Maharashtra", "Mumbai"),
    "pune": ("Maharashtra", "Pune"),
    "nagpur": ("Maharashtra", "Nagpur"),
    "aurangabad": ("Maharashtra", "Aurangabad"),

    # Gujarat
    "ahmedabad": ("Gujarat", "Ahmedabad"),
    "surat": ("Gujarat", "Surat"),
    "vadodara": ("Gujarat", "Vadodara"),
}


def detect_location_from_message(text: str):
    """Message mein location keywords dhundho"""
    text_lower = text.lower()
    for keyword, (state, district) in LOCATION_KEYWORDS.items():
        if keyword in text_lower:
            print(f"LOCATION FROM MESSAGE: {keyword} → {district}, {state}")
            return state, district
    return None, None


def detect_location_from_phone(phone: str):
    """Phone number se state/district detect karo"""
    # WhatsApp format: 91XXXXXXXXXX
    # Local number extract karo
    if phone.startswith("91") and len(phone) > 10:
        local = "0" + phone[2:]  # 91XXXXXXXXXX → 0XXXXXXXXXX

        # STD code match karo (longest match first)
        for std_code in sorted(PHONE_STATE_MAP.keys(), key=len, reverse=True):
            if local.startswith(std_code):
                state, district = PHONE_STATE_MAP[std_code]
                print(f"LOCATION FROM PHONE: {std_code} → {district}, {state}")
                return state, district

    return None, None


async def get_or_create_farmer(phone: str, name: str = "Kisan Bhai", message_text: str = "") -> dict:
    async with httpx.AsyncClient(timeout=10) as client:

        # ── Pehle check karo farmer exist karta hai ────────────
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers=HEADERS,
            params={"phone_number": f"eq.{phone}", "select": "*"},
        )

        if response.status_code == 200 and response.json():
            farmer = response.json()[0]
            print(f"FARMER FOUND: {phone}")

            existing_state = farmer.get("state", "")
            existing_district = farmer.get("district", "")

            # Agar message mein location hai toh update karo
            if message_text:
                msg_state, msg_district = detect_location_from_message(message_text)
                if msg_state and msg_district:
                    # Location update karo
                    await client.patch(
                        f"{SUPABASE_URL}/rest/v1/farmers",
                        headers={**HEADERS, "Prefer": "return=minimal"},
                        params={"phone_number": f"eq.{phone}"},
                        json={"state": msg_state, "district": msg_district},
                    )
                    existing_state = msg_state
                    existing_district = msg_district
                    print(f"LOCATION UPDATED: {msg_district}, {msg_state}")

            return {
                "phone": farmer.get("phone_number", phone),
                "name": farmer.get("name", name),
                "language": farmer.get("language", "Hindi"),
                "state": existing_state or "Jharkhand",
                "district": existing_district or "Ranchi",
                "plan": farmer.get("plan", "free"),
            }

        # ── Naya farmer — location detect karo ─────────────────
        print(f"FARMER NOT FOUND — creating: {phone}")

        # Priority: Message > Phone number > Default
        state, district = None, None

        # 1. Message se location
        if message_text:
            state, district = detect_location_from_message(message_text)

        # 2. Phone se location
        if not state:
            state, district = detect_location_from_phone(phone)

        # 3. Default (last resort)
        if not state:
            state, district = "Jharkhand", "Ranchi"
            print(f"LOCATION DEFAULT: {district}, {state}")

        new_farmer = {
            "phone_number": phone,
            "name": name,
            "language": "Hindi",
            "state": state,
            "district": district,
            "plan": "free",
        }

        insert_response = await client.post(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers=HEADERS,
            json=new_farmer,
        )

        print(f"FARMER SAVED: {insert_response.status_code} — {district}, {state}")

        return {
            "phone": phone,
            "name": name,
            "language": "Hindi",
            "state": state,
            "district": district,
            "plan": "free",
        }


async def update_farmer_location(phone: str, state: str, district: str):
    """Farmer ki location update karo"""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.patch(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers={**HEADERS, "Prefer": "return=minimal"},
            params={"phone_number": f"eq.{phone}"},
            json={"state": state, "district": district},
        )
        print(f"LOCATION UPDATE: {phone} → {district}, {state} ({resp.status_code})")


async def update_farmer_language(phone: str, language: str):
    """Farmer ki language update karo"""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.patch(
            f"{SUPABASE_URL}/rest/v1/farmers",
            headers={**HEADERS, "Prefer": "return=minimal"},
            params={"phone_number": f"eq.{phone}"},
            json={"language": language},
        )
        print(f"LANGUAGE UPDATE: {phone} → {language} ({resp.status_code})")
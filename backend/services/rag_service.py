import httpx
import json
import re
from config import settings

# ── Supabase REST headers ──────────────────────────────────────
def _sb_headers(service_key=False):
    key = settings.SUPABASE_SERVICE_KEY if service_key else settings.SUPABASE_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

# ── Simple keyword-based search (no heavy ML needed) ──────────
AGRI_KNOWLEDGE = {
    "pm kisan": """PM-KISAN Yojana ki poori jaankari:
• Labh: ₹6,000 per saal — 3 kiston mein (₹2,000 har 4 mahine)
• Kaun eligible hai: Sabhi chote aur seemaant kisan jinke paas 2 hectare tak zameen hai
• Zaruri documents: Aadhar card, bank account (Aadhar se linked), khasra/khatauni
• Registration: pmkisan.gov.in ya nazdiki CSC center
• Helpline: 155261 ya 1800-115-526 (toll free)
• Status check: pmkisan.gov.in/beneficiarystatus par jayen""",

    "pm-kisan": """PM-KISAN Yojana:
• ₹6,000/saal milte hain — 3 installments mein
• Register karein: pmkisan.gov.in
• Documents: Aadhar + Bank passbook + Khasra
• Helpline: 1800-115-526""",

    "fasal bima": """Pradhan Mantri Fasal Bima Yojana (PMFBY):
• Kharif faslon ke liye: 2% premium
• Rabi faslon ke liye: 1.5% premium
• Commercial/Horticulture: 5% premium
• Claim: Fasal kharab hone ke 72 ghante mein bank ko soochit karein
• Registration: Last date — Kharif ke liye July 31, Rabi ke liye December 31
• Apply: nazdiki bank ya insurance company mein""",

    "kcc": """Kisan Credit Card (KCC):
• Loan limit: ₹3 lakh tak
• Byaaj dar: Sirf 4% per saal (7% - 3% govt subsidy)
• Validity: 5 saal
• Kahan apply karein: SBI, PNB, Bank of Baroda, ya koi bhi cooperative bank
• Documents: Khasra, Aadhar, 2 photo, bank account
• Fasal ke hisaab se limit badhti hai""",

    "msp": """Minimum Support Price (MSP) 2024-25:
• Gehu: ₹2,275/quintal
• Dhan (Common): ₹2,300/quintal
• Sarson: ₹5,950/quintal
• Makka: ₹2,225/quintal
• Chana: ₹5,440/quintal
• MSP pe bechne ke liye: enam.gov.in ya nazdiki mandi
• Helpline: 1800-270-0224""",

    "urea": """Urea ki sahi jaankari:
• Maximum retail price: ₹242 per bag (45 kg) — zyada mat dena!
• Neem-coated urea use karein — zyada faaydemand hai
• Dose: Gehu mein 2-3 bag/acre, Dhan mein 2 bag/acre
• Kab daalein: Bawaai ke waqt + pehli sinchai ke baad
• Zyada urea nuksaan karta hai — soil test karwayein""",

    "dap": """DAP (Di-Ammonium Phosphate):
• Maximum price: ₹1,350 per bag (50 kg)
• Phosphorus aur Nitrogen dono milta hai
• Dose: 1 bag/acre bawaai ke waqt
• Gehu, Dhan, Sarson sab mein use hota hai
• Subsidy available hai — authorized dealer se lo""",

    "soil health": """Soil Health Card:
• Mitti ki poori jaanch FREE hoti hai
• NPK, pH, organic carbon sab pata chalta hai
• Kahan jayen: nazdiki Krishi Vigyan Kendra ya Krishi Vibhag
• Har 2 saal mein karwayein
• Card milne ke baad: fertilizer ki sahi matra pata chalegi""",

    "drip irrigation": """Drip Irrigation (Tanka Sinchai):
• Subsidy: 55-75% (SC/ST kisanon ke liye zyada)
• PM Krishi Sinchai Yojana ke tahat
• Pani ki 50-70% bachat hoti hai
• Apply: nazdiki Horticulture ya Agriculture department
• 1 acre drip system: ₹40,000-50,000 (subsidy ke baad ₹15,000-20,000)""",

    "gehu": """Gehu (Wheat) ki kheti — Chatra, Jharkhand:
• Variety: HD-2967, PBW-343, HI-8498 (best for Jharkhand)
• Bawaai time: October 15 - November 30
• Beej: 40-45 kg/acre
• Row spacing: 20-22 cm
• DAP: 1 bag/acre bawaai mein, Urea: 2 bag/acre (2 kiston mein)
• Sinchai: 4-5 baar (CRI, tillering, jointing, flowering, grain filling)
• Yield: 15-20 quintal/acre""",

    "dhan": """Dhan (Rice/Paddy) ki kheti:
• Variety: Swarna, MTU-7029, Sahbhagi (drought tolerant)
• Nursery: June 1-15, Transplanting: July 1-20
• Spacing: 20x15 cm
• Pani ka level: 5 cm rakhen
• Zinc sulphate: 10 kg/acre zaroor daalein
• Urea: 2.5 bag/acre (3 kiston mein)
• Yield: 20-25 quintal/acre""",

    "sarson": """Sarson (Mustard) ki kheti:
• Variety: Pusa Bold, Pusa Agrani
• Bawaai: October mein
• Beej: 1.5-2 kg/acre
• Aphid keeda: Imidacloprid 0.5ml/litre spray karein
• Yield: 6-8 quintal/acre
• MSP: ₹5,950/quintal""",

    "bimari": """Fasal mein bimari — Common problems:
• Patte peele hone: Nitrogen ki kami — Urea spray (2%)
• Patte par dhabbe: Fungal infection — Mancozeb ya Carbendazim spray
• Jad sadna: Waterlogging — drainage theek karein
• Blast disease (Dhan): Tricyclazole spray
• Organic solution: Neem oil 5ml/litre spray""",

    "keeda": """Keedon se bachav:
• Organic: Neem oil 5ml + 1ml liquid soap per litre pani
• Chemical: Imidacloprid, Chlorpyrifos, Cypermethrin
• Spray time: Subah ya shaam (dhoop mein mat karein)
• Barish se pehle spray mat karein
• IPM apnayein — phande (traps) use karein""",

    "subsidy": """Kisanon ke liye Subsidies:
• Urea: ₹242/bag fixed price (heavy subsidy)
• DAP: ₹1,350/bag (subsidized)
• Drip/Sprinkler: 55-75% subsidy
• Solar pump: 60-70% subsidy (PM KUSUM)
• Beej: 50% subsidy certified beej par
• Tractor: 25-50% subsidy (state schemes)
• Apply: nazdiki Krishi Vibhag mein""",

    "mausam": """Mausam aur kheti:
• Barish se pehle chhidkav mat karein — dawai beh jaati hai
• Tej garmi mein: Subah 7-9 baje ya shaam 5-7 baje spray karein
• Aandhi/Tufan warning: Sinchai band karein, drainage kholo
• Drought mein: Mulching karein, drip use karein
• Mausam update: Meghdoot app download karein (free)""",
}

async def retrieve_context(query: str) -> str:
    """
    2-step retrieval:
    1. Pehle local knowledge base mein dhundho (fast)
    2. Phir Supabase documents table mein dhundho (agar local mein na mile)
    """
    query_lower = query.lower()

    # ── Step 1: Local knowledge base ──────────────────────────
    best_match = ""
    best_score = 0

    for key, value in AGRI_KNOWLEDGE.items():
        # Score calculate karo — kitne keywords match hue
        key_words = key.split()
        score = sum(1 for word in key_words if word in query_lower)
        if score > best_score:
            best_score = score
            best_match = value

    if best_score > 0:
        print(f"RAG LOCAL HIT: score={best_score}")
        return best_match

    # ── Step 2: Supabase documents table mein text search ─────
    try:
        context = await search_documents(query)
        if context:
            print(f"RAG DB HIT: found in documents table")
            return context
    except Exception as e:
        print(f"RAG DB ERROR: {e}")

    return "Krishi Vigyan Kendra se milkar salah lein. Helpline: 1800-180-1551"


async def search_documents(query: str) -> str:
    """Supabase documents table mein full-text search"""
    try:
        # Simple text search using ilike
        words = query.lower().split()[:3]  # First 3 words use karo

        for word in words:
            if len(word) < 4:  # Chhote words skip karo
                continue
            url = (
                f"{settings.SUPABASE_URL}/rest/v1/documents"
                f"?content=ilike.*{word}*"
                f"&select=content,metadata"
                f"&limit=1"
            )
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers=_sb_headers())
                rows = resp.json()
                if rows and len(rows) > 0:
                    content = rows[0].get("content", "")
                    if len(content) > 100:
                        # First 500 chars return karo
                        return content[:500] + "..."

        return ""
    except Exception as e:
        print(f"SEARCH ERROR: {e}")
        return ""


async def add_document(content: str, metadata: dict = {}) -> bool:
    """
    Naya document add karo Supabase mein
    (PDF upload karne ke baad use karein)
    """
    try:
        # Content ko chunks mein todo (500 words each)
        chunks = split_into_chunks(content, chunk_size=500)

        async with httpx.AsyncClient(timeout=30) as client:
            for i, chunk in enumerate(chunks):
                data = {
                    "content": chunk,
                    "metadata": {**metadata, "chunk": i, "total_chunks": len(chunks)},
                }
                url = f"{settings.SUPABASE_URL}/rest/v1/documents"
                headers = {**_sb_headers(service_key=True), "Prefer": "return=minimal"}
                resp = await client.post(url, headers=headers, json=data)
                print(f"CHUNK {i+1}/{len(chunks)} saved: {resp.status_code}")

        return True
    except Exception as e:
        print(f"ADD DOCUMENT ERROR: {e}")
        return False


def split_into_chunks(text: str, chunk_size: int = 500) -> list:
    """Text ko chhote chunks mein todo"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


async def upload_pdf_to_rag(pdf_path: str, source_name: str) -> bool:
    """
    PDF file ko read karo aur RAG mein add karo
    Usage: await upload_pdf_to_rag("pm_kisan.pdf", "PM-KISAN Scheme")
    """
    try:
        import PyPDF2

        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"

        print(f"PDF READ: {len(text)} characters from {source_name}")

        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()

        # Add to database
        success = await add_document(
            content=text,
            metadata={"source": source_name, "type": "pdf"}
        )

        if success:
            print(f"PDF UPLOADED: {source_name} ✅")
        return success

    except Exception as e:
        print(f"PDF UPLOAD ERROR: {e}")
        return False
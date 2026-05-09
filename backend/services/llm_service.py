import httpx
from config import settings

SYSTEM_PROMPT = """
You are Kisan Saathi AI — India's most helpful and friendly agricultural assistant for farmers.

YOUR PERSONALITY:
- Warm, caring, and respectful like a knowledgeable friend
- Use "ji" respectfully (Namaste ji, Aap ji, etc.)
- Never give one-line answers — always give complete helpful info

CRITICAL LANGUAGE RULES — FOLLOW EXACTLY:
- Detect language from the farmer's EXACT message
- Hindi message → Reply ONLY in Hindi (Devanagari or Roman Hindi)
- English message → Reply ONLY in English
- Hinglish message → Reply in Hinglish
- Bhojpuri/dialect → Reply in simple Hindi
- NEVER mix languages unless farmer does
- NEVER switch language mid-response
- Test: If farmer writes "What is MSP?" → Reply in English ONLY
- Test: If farmer writes "MSP kya hai?" → Reply in Hindi ONLY

CRITICAL WEATHER RULE:
- Agar weather/mausam ka sawal aaye → DIRECTLY jawab do farmer ki location ke hisaab se
- KABHI MAT KAHO "dusri site pe jao" ya "search karo"
- Context mein weather data diya gaya hai — use karo
- Agar exact data nahi hai toh bhi seasonal advice do unki location ke hisaab se

CRITICAL CROP RULE:
- Jo crop farmer ne mention kiya SIRF usi ke baare mein batao
- Wheat poochha → Sirf wheat batao — sugarcane, rice mat batao
- Gehu poochha → Gehu ki hi jaankari do
- Dhan poochha → Dhan/rice ki jaankari do

SIMPLIFICATION RULE:
- Agar farmer kahe "nahi samjha", "dobara batao", "simple mein" →
  Same info ko aur chhote sentences mein, example ke saath dobara do

RESPONSE QUALITY:
- Structured responses with clear sections
- Emojis for friendly tone
- Specific numbers, prices, quantities
- Always explain WHY

FOR CROP CALENDAR ("calendar banao", "schedule"):
📅 *[Crop] Crop Calendar ([Location])*
─────────────────
*Month* → Kaam karna hai
(Month by month table)

FOR BUDGET/PROFIT ("budget", "profit", "kitna kharcha"):
💰 *[Crop] Budget (1 Acre)*
─────────────────
*Kharcha:*
• Item: ₹Amount
─────────────────
*Total Kharcha: ₹X*
*Expected Kamai: ₹Y*
*Net Profit: ₹Z* ✅

FOR GOVERNMENT SCHEMES:
- Scheme name, benefit amount, eligibility
- Step-by-step application
- Documents required
- Helpline number

FOR DISEASE/PEST:
- Problem clearly identify karo
- Chemical AND organic solution
- Dosage and method
- Prevention

ALWAYS END WITH:
- One actionable tip for today
- "Aur koi sawal? Main hamesha aapki madad ke liye hoon! 🌾"

RESPONSE FORMAT:
🌾 [Topic Heading]

📊 [Main Information]

✅ Aapke liye Sujhav:
• [Tip 1]
• [Tip 2]
• [Tip 3]

⚡ Aaj ka Action:
[One thing to do today]

Aur koi sawal? Main hamesha aapki madad ke liye hoon! 🌾
"""


async def generate_response(
    user_message: str,
    context: str = "",
    farmer: dict = {},
    intent: str = "general",
    chat_history: list = []
) -> str:

    name = farmer.get("name", "Kisan Bhai")
    state = farmer.get("state", "Jharkhand")
    district = farmer.get("district", "Chatra")
    language = farmer.get("language", "Hindi")

    # Language detect karo message se
    detected_lang = detect_language(user_message)

    user_prompt = f"""
Farmer Details:
- Name: {name}
- Location: {district}, {state}
- Message Language Detected: {detected_lang}
- Intent: {intent}

Context/Data Available:
{context if context else "No additional context — use your knowledge"}

Farmer's Message: {user_message}

STRICT Instructions:
1. Reply in {detected_lang} ONLY — match the farmer's language exactly
2. Give COMPLETE, SATISFYING response
3. Be specific to {district}, {state}
4. If intent is weather — give direct weather advice, NEVER say "visit another site"
5. If a specific crop is mentioned — talk ONLY about that crop
6. Use structured format with emojis
7. If farmer says "nahi samjha" → simplify with examples
"""

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for h in chat_history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})

    messages.append({"role": "user", "content": user_prompt})

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1200,
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


def detect_language(text: str) -> str:
    """Message ki language detect karo"""
    text_lower = text.lower()

    # English words check
    english_words = [
        "what", "how", "when", "where", "why", "which", "who",
        "is", "are", "the", "for", "and", "crop", "farm",
        "weather", "price", "disease", "scheme", "loan"
    ]
    english_count = sum(1 for w in english_words if w in text_lower.split())

    # Hindi/Devanagari check
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')

    if hindi_chars > 3:
        return "Hindi"
    elif english_count >= 2:
        return "English"
    else:
        # Hinglish common words
        hinglish_words = [
            "kya", "hai", "mein", "ka", "ki", "ke", "se",
            "aur", "nahi", "kaise", "kitna", "kab", "kahan",
            "batao", "bolo", "help", "please", "mera", "meri"
        ]
        hinglish_count = sum(1 for w in hinglish_words if w in text_lower.split())
        if hinglish_count >= 1:
            return "Hinglish"

    return "Hindi"  # Default Hindi
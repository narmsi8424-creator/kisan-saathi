from groq import Groq
import os
import base64

async def speech_to_text(audio_bytes: bytes, language: str = "hi") -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Save audio temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name
        
        with open(temp_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=("audio.ogg", f.read()),
                model="whisper-large-v3",
                language=language,
                response_format="text"
            )
        
        import os as _os
        _os.unlink(temp_path)
        return transcription
        
    except Exception as e:
        return ""

async def translate_text(text: str, source_lang: str, target_lang: str = "hi") -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Translate this to Hindi: {text}. Only give translation, nothing else."
            }],
            max_tokens=200
        )
        return response.choices[0].message.content
    except:
        return text

async def detect_language(text: str) -> str:
    devanagari = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    if devanagari > len(text) * 0.3:
        return "hi"
    return "en"
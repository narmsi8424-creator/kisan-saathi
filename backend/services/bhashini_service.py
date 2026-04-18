async def speech_to_text(audio_bytes: bytes, language: str = "hi") -> str:
    return "Meri fasal mein bimari lag gayi hai"

async def translate_text(text: str, source_lang: str, target_lang: str = "hi") -> str:
    return text

async def detect_language(text: str) -> str:
    devanagari = sum(1 for c in text if "\u0900" <= c <= "\u097F")
    if devanagari > len(text) * 0.3:
        return "hi"
    return "en"
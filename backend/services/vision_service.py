import httpx
import os
import base64
import json

async def analyze_plant_image(image_data: bytes = None, image_url: str = None) -> str:
    try:
        api_key = os.getenv("GROQ_API_KEY")
        
        b64 = base64.b64encode(image_data).decode() if image_data else None
        
        if not b64:
            return "Photo receive nahi hui. Dobara bhejein."

        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Aap ek expert Indian agricultural scientist hain.
Is photo ka analysis karein aur Hindi mein jawab dein:

Agar photo mein fasal/plant hai:
1. Kya bimari ya keeda hai (naam batayein)
2. Kya karan hai
3. Kya ilaaj karein (dawa ka naam aur matra)
4. Aage kaise bachayein

Agar fasal nahi hai:
- Batayein ki photo mein kya dikh raha hai
- Farming se related koi advice dein

Short aur clear jawab dein."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 600,
            "temperature": 0.3,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            data = response.json()
            print(f"VISION API STATUS: {response.status_code}")
            print(f"VISION API RESPONSE: {str(data)[:200]}")
            
            if response.status_code == 200:
                return data["choices"][0]["message"]["content"].strip()
            else:
                print(f"VISION ERROR: {data}")
                return (
                    "📸 Photo analysis mein error aaya.\n\n"
                    "🌾 Text mein batayen:\n"
                    "- Patte ka rang kaisa hai?\n"
                    "- Dhabbe hain ya nahi?\n"
                    "- Koi keeda dikh raha hai?"
                )

    except Exception as e:
        print(f"VISION EXCEPTION: {e}")
        return (
            "📸 Photo analysis abhi available nahi hai.\n\n"
            "🌾 Bimari ke lakshan batayein text mein:\n"
            "- Patte ka rang kaisa hai?\n"
            "- Dhabbe hain ya nahi?\n"
            "- Koi keeda dikh raha hai?\n\n"
            "Main text se bhi bimari pehchaan sakta hoon!"
        )
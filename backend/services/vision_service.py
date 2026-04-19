from groq import Groq
import os
import base64

async def analyze_plant_image(image_data: bytes = None, image_url: str = None) -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Aap ek expert Indian agricultural scientist hain.
                        Is photo mein jo fasal dikh rahi hai uski bimari ya keede ka analysis karein.
                        Hindi mein jawab dein aur batayein:
                        1. Kya bimari/keeda hai
                        2. Kya karan hai
                        3. Kya ilaaj karein (dawa ka naam)
                        4. Kaise bachayein aage se
                        Agar photo mein fasal nahi hai toh batayein."""
                    }
                ]
            }
        ]
        
        if image_data:
            b64 = base64.b64encode(image_data).decode()
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })
        
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return (
            "📸 Photo analysis abhi available nahi hai.\n\n"
            "🌾 Bimari ke lakshan batayein text mein:\n"
            "- Patte ka rang kaisa hai?\n"
            "- Dhabbe hain ya nahi?\n"
            "- Koi keeda dikh raha hai?\n\n"
            "Main text se bhi bimari pehchaan sakta hoon!"
        )
import httpx
from datetime import date

async def get_mandi_prices(crop="wheat", state="Bihar"):
    today = date.today().strftime("%d/%m/%Y")
    mock = {
        "wheat":   (2100, 2250, 2180),
        "gehu":    (2100, 2250, 2180),
        "mustard": (4800, 5200, 5050),
        "sarson":  (4800, 5200, 5050),
        "potato":  (900,  1200, 1050),
        "aloo":    (900,  1200, 1050),
        "paddy":   (1700, 1900, 1815),
        "dhan":    (1700, 1900, 1815),
        "onion":   (1500, 2000, 1750),
        "pyaz":    (1500, 2000, 1750),
        "tomato":  (800,  1500, 1150),
        "tamatar": (800,  1500, 1150),
    }
    mn, mx, md = mock.get(crop.lower(), (1500, 2000, 1750))
    return (
        f"📊 *{crop.title()} — {state} Mandi Rates*\n"
        f"📅 Date: {today}\n\n"
        f"⬇️ Min: ₹{mn}/quintal\n"
        f"⬆️ Max: ₹{mx}/quintal\n"
        f"✅ Modal: ₹{md}/quintal\n\n"
        f"💡 *Salah:* Subah 8-10 baje becho!\n"
        f"Aur koi sawal? Mujhe batao! 🌱"
    )
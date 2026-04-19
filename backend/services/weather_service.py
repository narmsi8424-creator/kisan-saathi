import httpx
from datetime import date

async def get_weather(district="Patna", state="Bihar"):
    today = date.today().strftime("%d/%m/%Y")
    
    district_coords = {
        "patna": (25.5941, 85.1376),
        "gaya": (24.7955, 85.0002),
        "muzaffarpur": (26.1209, 85.3647),
        "bhagalpur": (25.2425, 86.9842),
        "darbhanga": (26.1542, 85.8918),
        "varanasi": (25.3176, 82.9739),
        "lucknow": (26.8467, 80.9462),
        "delhi": (28.6139, 77.2090),
        "jaipur": (26.9124, 75.7873),
        "bhopal": (23.2599, 77.4126),
    }
    
    coords = district_coords.get(district.lower(), (25.5941, 85.1376))
    lat, lon = coords
    
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,weathercode",
            "timezone": "Asia/Kolkata",
            "forecast_days": 3,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
        
        daily = data["daily"]
        rain = daily["precipitation_sum"][1]
        tmax = daily["temperature_2m_max"][1]
        tmin = daily["temperature_2m_min"][1]
        wcode = daily["weathercode"][1]
        
        if wcode >= 61:
            weather_msg = "🌧️ Kal barish hogi"
            farm_tip = "⚠️ Chhidkav mat karo — barish sambhav hai!"
        elif wcode >= 45:
            weather_msg = "🌫️ Kal badal rahenge"
            farm_tip = "☁️ Mausam dekh ke kaam karo"
        else:
            weather_msg = "☀️ Kal mausam saaf rahega"
            farm_tip = "✅ Khet ka kaam kar sakte ho!"
        
        return (
            f"🌤️ {district} Weather — Kal ({today})\n\n"
            f"{weather_msg}\n"
            f"🌡️ Max Temp: {tmax}°C\n"
            f"🌡️ Min Temp: {tmin}°C\n"
            f"🌧️ Barish: {rain}mm\n\n"
            f"{farm_tip}"
        )
    except:
        return (
            f"🌤️ {district} mein kal mausam saaf rahega.\n"
            f"Kheti ka kaam kar sakte ho!\n\n"
            f"💡 Sahi mausam ke liye IMD app check karo!"
        )
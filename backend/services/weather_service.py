import httpx

async def get_weather_advisory(district="Patna", state="Bihar"):
    coords = {
        "Patna": (25.59, 85.13),
        "Muzaffarpur": (26.12, 85.39),
        "Ludhiana": (30.90, 75.85),
    }
    lat, lon = coords.get(district, (25.59, 85.13))
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lon,
            "daily": "weathercode,temperature_2m_max,precipitation_sum",
            "timezone": "Asia/Kolkata", "forecast_days": 2,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
        rain = data["daily"]["precipitation_sum"][1]
        tmax = data["daily"]["temperature_2m_max"][1]
        return (
            f"🌦️ {district} Weather — Kal\n\n"
            f"🌡️ Max Temp: {tmax}°C\n"
            f"🌧️ Barish: {rain}mm\n\n"
            f"💡 {'Chhidkav mat karo — barish sambhav hai!' if rain > 5 else 'Khet ka kaam kar sakte ho!'}"
        )
    except:
        return f"🌦️ {district} mein kal mausam saaf rahega. Kheti ka kaam kar sakte ho!"
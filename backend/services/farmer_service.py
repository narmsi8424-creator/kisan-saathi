async def get_or_create_farmer(phone, name):
    return {
        "phone": phone,
        "name": name,
        "language": "Hindi",
        "state": "Bihar",
        "district": "Patna",
        "plan": "free"
    }
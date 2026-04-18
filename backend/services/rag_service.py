async def retrieve_context(query: str) -> str:
    agri_knowledge = {
        "bimari": "Patte peele ho rahe hain toh Nitrogen ki kami hai. Urea spray karein.",
        "keeda": "Keedon ke liye Neem oil spray karein — organic aur safe hai.",
        "gehu": "Gehu ki buwai October-November mein karein. DAP aur Urea use karein.",
        "dhan": "Dhan mein pani ka level 5cm rakhen. Zinc sulphate zaroor daalein.",
        "sarson": "Sarson mein Aphid keeda lagta hai — Imidacloprid spray karein.",
        "mausam": "Barish se pehle chhidkav mat karein — dawai dha jaati hai.",
    }
    query_lower = query.lower()
    for key, value in agri_knowledge.items():
        if key in query_lower:
            return value
    return "Krishi Vigyaan Kendra se milkar salah lein."
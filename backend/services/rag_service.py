async def retrieve_context(query: str) -> str:
    agri_knowledge = {
        "bimari": "Patte peele ho rahe hain toh Nitrogen ki kami hai. Urea spray karein.",
        "keeda": "Keedon ke liye Neem oil spray karein — organic aur safe hai.",
        "gehu": "Gehu ki buwai October-November mein karein. DAP aur Urea use karein.",
        "dhan": "Dhan mein pani ka level 5cm rakhen. Zinc sulphate zaroor daalein.",
        "sarson": "Sarson mein Aphid keeda lagta hai — Imidacloprid spray karein.",
        "mausam": "Barish se pehle chhidkav mat karein — dawai dha jaati hai.",
        "pm kisan": "PM-KISAN mein 6000 rupaye saal mein milte hain — 3 kiston mein. Aadhar aur bank account link hona chahiye. Register karein: pmkisan.gov.in",
        "pm-kisan": "PM-KISAN mein 6000 rupaye saal mein milte hain — 3 kiston mein. pmkisan.gov.in pe register karein.",
        "kisan": "PM-KISAN scheme mein ₹6000/saal milte hain. Fasal Bima Yojana mein fasal ka bima hota hai.",
        "fasal bima": "Pradhan Mantri Fasal Bima Yojana mein fasal kharab hone pe muavza milta hai. Premium bahut kam hai — Rabi mein 1.5%, Kharif mein 2%.",
        "bima": "PMFBY mein fasal ka bima karwao — Kharif ke liye July tak, Rabi ke liye December tak.",
        "loan": "Kisan Credit Card (KCC) se 3 lakh tak ka loan 4% byaaj mein milta hai. Nazdiki bank mein apply karein.",
        "kcc": "Kisan Credit Card se sasta loan milta hai — 4% interest rate. SBI, PNB, kisi bhi bank mein apply karein.",
        "subsidy": "Khad (fertilizer) pe 50% subsidy milti hai. Beej pe bhi subsidy hai — Krishi Vibhag se sampark karein.",
        "urea": "Urea ki maximum retail price ₹242/bag (45kg) hai — zyada nahi dena. Neem-coated urea use karein.",
        "yojana": "Mukhya yojanaen: PM-KISAN (₹6000/saal), PMFBY (Fasal Bima), KCC (Sasta Loan), Soil Health Card.",
        "soil": "Soil Health Card ke liye nazdiki Krishi Kendra mein jayen — mitti ki jaanch free hoti hai.",
        "drip": "Drip irrigation pe 55-75% subsidy milti hai. Pradhan Mantri Krishi Sinchai Yojana ke tahat.",
    }
    
    query_lower = query.lower()
    for key, value in agri_knowledge.items():
        if key in query_lower:
            return value
    return "Krishi Vigyaan Kendra se milkar salah lein."
def categorize_transaction(description: str) -> dict:
    """Categorize a transaction using simple merchant rules."""

    text = description.upper()

    category_rules = {
        "Income": [
            "SALARY",
            "CREDIT",
        ],
        "Housing": [
            "RENT",
        ],
        "Food": [
            "SWIGGY",
            "ZOMATO",
            "DOMINOS",
            "RESTAURANT",
        ],
        "Transport": [
            "UBER",
            "OLA",
            "PETROL",
            "FUEL",
        ],
        "Shopping": [
            "AMAZON",
            "FLIPKART",
            "MYNTRA",
        ],
        "Utilities": [
            "ELECTRICITY",
            "WATER BILL",
            "GAS BILL",
            "MOBILE RECHARGE",
            "PHONE BILL",
            "INTERNET",
        ],
        "Entertainment": [
            "NETFLIX",
            "SPOTIFY",
            "PRIME VIDEO",
        ],
        "Health & Fitness": [
            "GYM",
            "PHARMACY",
            "HOSPITAL",
        ],
        "Groceries": [
            "GROCERY",
            "SUPERMARKET",
        ],
        "Vacation & Travel": [
            "HOTEL",
            "AIRLINE",
            "TRAVEL",
            "TOUR",
            "VACATION",
        ],
    }

    for category, keywords in category_rules.items():
        for keyword in keywords:
            if keyword in text:
                return {
                    "category": category,
                    "confidence": 1.0,
                }

    return {
        "category": "Other",
        "confidence": 0.5,
    }
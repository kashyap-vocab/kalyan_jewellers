@tool
def gold_price_data(query: str) -> str:
    """
    Matches user query with price data programmatically for better accuracy.
    """
    try:
        prices = get_cached_prices()

        # crude parsing to detect purity and metal type
        query_lower = query.lower()

        metal = "gold" if "gold" in query_lower else "silver"
        metal_data = prices.get(metal, {})

        # default to 22kt gold or 999 fine silver if no purity is mentioned
        purity = "22kt" if metal == "gold" else "999 fine (rs ₹)"
        for key in metal_data:
            if key.lower().replace(" ", "") in query_lower.replace(" ", ""):
                purity = key
                break

        weight = "1 gram"
        for option in ["1 gram", "10 gram", "100 gram", "1 kilogram", "1 ounce", "1 tola"]:
            if option in query_lower:
                weight = option
                break

        rate = metal_data.get(purity, {}).get(weight)
        if rate:
            return f"Today's price for {purity} {metal} ({weight}) is ₹{rate}."
        else:
            return f"Sorry, I don't have the price for {purity} {metal} per {weight}."

    except Exception as e:
        return f"Error fetching price: {e}"

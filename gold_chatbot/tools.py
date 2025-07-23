import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googleapiclient.discovery import build
from langchain.tools import Tool

load_dotenv()

VALID_CARATS = [24, 22, 20, 18, 14, 10, 6]


def extract_gold_price_bullions(karat: str, weight_grams: int) -> str:
    try:
        url = "https://bullions.co.in/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the gold price table
        table = soup.find("table", class_="data")
        rows = table.find("tbody").find_all("tr")

        karat = karat.strip().lower().replace("kt", "karat").replace("ct", "karat")

        # Find the row matching the required karat
        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue
            karat_name = cols[0].text.strip().lower()
            if karat in karat_name:
                if weight_grams == 1:
                    price = cols[1].text
                elif weight_grams == 10:
                    price = cols[2].text
                elif weight_grams == 100:
                    price = cols[3].text
                elif weight_grams == 1000:
                    price = cols[4].text
                else:
                    return f"Weight {weight_grams}g not available. Try 1g, 10g, 100g, or 1kg."
                return f"Price of {weight_grams}g {karat.title()} gold today is ₹{price}."
        return f"{karat.title()} gold not found on the site."
    except Exception as e:
        return f"Error fetching price: {str(e)}"

def extract_silver_price(weight_grams: int, purity: str = "999") -> str:
    try:
        url = "https://bullions.co.in/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all pricing tables and assume second one is silver
        tables = soup.find_all("table", class_="data")
        if len(tables) < 2:
            return "Silver pricing table not found on the site."

        silver_table = tables[1]  # Silver is usually the second table
        rows = silver_table.find("tbody").find_all("tr")

        purity = purity.strip()
        purity_match = f"silver {purity}"  # e.g., silver 999

        # Match row by purity level (e.g., "Silver 999 Fine")
        for row in rows:
            cols = row.find_all("td")
            if not cols:
                continue
            purity_name = cols[0].text.strip().lower()
            if purity_match in purity_name:
                if weight_grams == 1:
                    price = cols[1].text.strip()
                elif weight_grams == 10:
                    price = cols[2].text.strip()
                elif weight_grams == 100:
                    price = cols[3].text.strip()
                elif weight_grams == 1000:
                    price = cols[4].text.strip()
                else:
                    return f"Unsupported weight: {weight_grams}g. Try 1g, 10g, 100g, or 1000g."

                return f"💰 Price of {weight_grams}g Silver ({purity} purity) today is ₹{price}."

        return f"No matching silver purity ({purity}) found."

    except Exception as e:
        return f"⚠️ Error fetching silver price: {str(e)}"


def metal_search(query: str) -> str:
    try:
        # Extract info from query
        weight_match = re.search(r'(\d+(\.\d+)?)\s*(g|gram|grams)', query.lower())
        carat_match = re.search(r'(\d+(\.\d+)?)\s*(ct|karat|kt|purity)', query.lower())
        metal_match = re.search(r'(gold|silver|platinum|palladium)', query.lower())

        weight = int(float(weight_match.group(1))) if weight_match else 1
        carat_or_purity = int(float(carat_match.group(1))) if carat_match else 999
        metal = metal_match.group(1).lower() if metal_match else "gold"

        if metal == "gold":
            if carat_or_purity not in VALID_CARATS:
                return (
                    f"Unsupported gold carat: {carat_or_purity}ct\n"
                    f"Try one of: {', '.join(map(str, VALID_CARATS))}ct"
                )
            return extract_gold_price_bullions(str(carat_or_purity), weight)

        elif metal == "silver":
            return extract_silver_price(weight_grams=weight, purity=str(carat_or_purity))

        else:
            return f"Sorry, {metal.title()} prices are not supported yet."

    except Exception as e:
        return f"[DEBUG ERROR] {str(e)}"


# LangChain Tool wrapper
gold_search_tool = Tool.from_function(
    func=metal_search,
    name="gold_price_search",
    description=(
        "Fetch current pricing of metals like gold, silver, platinum, etc., using real-time search. "
        "Query format examples: '8g 22ct gold price', '100g 6ct gold rate today', 'silver rate today 10g'."
    )
)

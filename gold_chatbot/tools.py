# # import os
# # from googleapiclient.discovery import build
# # from langchain.tools import Tool
# # from dotenv import load_dotenv
# # from datetime import datetime

# # load_dotenv()

# # def gold_search(query: str) -> str:
# #     api_key = os.getenv("GOOGLE_API_KEY")
# #     cx_id = os.getenv("GOOGLE_CX_ID")

# #     if not api_key or not cx_id:
# #         return "Error: GOOGLE_API_KEY and/or GOOGLE_CX_ID not set in .env"

# #     try:
# #         service = build("customsearch", "v1", developerKey=api_key)
# #         res = service.cse().list(q=query, cx=cx_id, num=5).execute()

# #         items = res.get("items", [])
# #         if not items:
# #             return f"No results found for: {query}"

# #         # Relax filtering: only exclude results if absolutely no items
# #         # Instead of filtering, just sort or prioritize items containing some keywords
# #         keywords = ["today", "live", "current", str(datetime.now().year)]

# #         # Separate items containing keywords vs others
# #         prioritized = []
# #         others = []
# #         for item in items:
# #             snippet = item.get("snippet", "").lower()
# #             title = item.get("title", "").lower()
# #             if any(kw in snippet or kw in title for kw in keywords):
# #                 prioritized.append(item)
# #             else:
# #                 others.append(item)

# #         # If no prioritized items found, fall back to all items
# #         filtered_items = prioritized if prioritized else items

# #         # Format and return output
# #         output = []
# #         for item in filtered_items:
# #             title = item.get("title", "")
# #             snippet = item.get("snippet", "")
# #             link = item.get("link", "")
# #             output.append(f"🔹 {title}\n{snippet}\n📎 {link}")

# #         return "\n\n".join(output)

# #     except Exception as e:
# #         return f"Error using Google Search API: {str(e)}"
    
# # gold_search_tool = Tool.from_function(
# #     func=gold_search,
# #     name="gold_price_search",
# #     description=(
# #         "Use this tool to fetch the current gold price, "
# #         "live gold rate, or jewellery-related information from the web. "
# #         "Provide a clear query like 'gold price today' or '22 carat gold rate in India'."
# #     )
# # )

# import os
# from googleapiclient.discovery import build
# from langchain.tools import Tool
# from dotenv import load_dotenv
# from datetime import datetime
# import re

# load_dotenv()

# def gold_search(query: str) -> str:
#     api_key = os.getenv("GOOGLE_API_KEY")
#     cx_id = os.getenv("GOOGLE_CX_ID")

#     if not api_key or not cx_id:
#         return "Error: GOOGLE_API_KEY and/or GOOGLE_CX_ID not set in .env"

#     try:
#         service = build("customsearch", "v1", developerKey=api_key)
#         res = service.cse().list(q=query, cx=cx_id, num=5).execute()

#         items = res.get("items", [])
#         if not items:
#             return f"No results found for: {query}"

#         # Relax filtering: return all items without filtering to maximize results
#         filtered_items = items

#         # Format and return output
#         output = []
#         for item in filtered_items:
#             title = item.get("title", "")
#             snippet = item.get("snippet", "")
#             link = item.get("link", "")
#             output.append(f"🔹 {title}\n{snippet}\n📎 {link}")

#         return "\n\n".join(output)

#     except Exception as e:
#         return f"Error using Google Search API: {str(e)}"


# gold_search_tool = Tool.from_function(
#     func=gold_search,
#     name="gold_price_search",
#     description=(
#         "Use this tool to fetch the current price or live rate of precious metals "
#         "like gold, silver, platinum etc., including different carats such as 22ct, 24ct, 18ct, and more. "
#         "Provide clear queries like 'gold price today', '24 carat silver rate in India', or 'platinum price 18ct'."
#     )
# )

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

def gold_search(query: str) -> str:
    try:
        # Extract weight, carat, and metal from the query
        weight_match = re.search(r'(\d+(\.\d+)?)\s*(g|gram|grams)', query.lower())
        carat_match = re.search(r'(\d+(\.\d+)?)\s*(ct|karat|kt)', query.lower())
        metal_match = re.search(r'(gold|silver|platinum|palladium)', query.lower())

        weight = int(float(weight_match.group(1))) if weight_match else 1
        carat = int(float(carat_match.group(1))) if carat_match else 24
        metal = metal_match.group(1).lower() if metal_match else "gold"

        if metal != "gold":
            return f"Sorry, only gold prices are currently supported via bullions.co.in."

        if carat not in VALID_CARATS:
            return (
                f"Unsupported carat value: {carat}ct\n"
                f"Please choose from common options: {', '.join(map(str, VALID_CARATS))}ct"
            )

        return extract_gold_price_bullions(str(carat), weight)

    except Exception as e:
        return f"[DEBUG ERROR] {str(e)}"

# LangChain Tool wrapper
gold_search_tool = Tool.from_function(
    func=gold_search,
    name="gold_price_search",
    description=(
        "Fetch current pricing of metals like gold, silver, platinum, etc., using real-time search. "
        "Query format examples: '8g 22ct gold price', '100g 6ct gold rate today', 'silver rate today 10g'."
    )
)

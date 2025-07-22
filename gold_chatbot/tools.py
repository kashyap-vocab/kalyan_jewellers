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

def extract_price_from_goodreturns(url: str, carat: float = 24.0) -> float:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        # Find first national price row
        row = soup.find("tr", class_=lambda c: c and c.endswith("ratesrow"))
        if not row:
            raise ValueError("Could not find pricing row.")

        cells = row.find_all("td")
        if len(cells) < 2:
            raise ValueError("Unexpected table format.")

        # GoodReturns shows ₹X,XXX/10g
        raw = cells[1].get_text().split("/")[0].replace("₹", "").replace(",", "")
        rate_per_10g = float(raw)
        rate_per_gram_24ct = rate_per_10g / 10

        # Adjust for carat purity
        purity = carat / 24.0
        return rate_per_gram_24ct * purity

    except Exception as e:
        raise RuntimeError(f"Failed to parse {url}: {e}")


def gold_search(query: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")

    if not api_key or not cx_id:
        return "Error: GOOGLE_API_KEY and/or GOOGLE_CX_ID not set in .env"

    try:
        # Extract weight, carat, metal
        weight_match = re.search(r'(\d+(\.\d+)?)\s*(g|gram)', query.lower())
        carat_match = re.search(r'(\d+(\.\d+)?)\s*ct', query.lower())
        metal_match = re.search(r'(gold|silver|platinum|palladium)', query.lower())

        weight = float(weight_match.group(1)) if weight_match else 8.0
        carat = float(carat_match.group(1)) if carat_match else 24.0
        metal = metal_match.group(1).lower() if metal_match else "gold"

        if carat not in VALID_CARATS:
            return (
                f"Unsupported carat value: {carat}ct\n"
                f"Please choose from common options: {', '.join(map(str, VALID_CARATS))}ct"
            )

        # Step 1: Search Google
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=f"{metal} price today", cx=cx_id, num=5).execute()
        items = res.get("items", [])

        if not items:
            return f"🔍 No results found for: {query}"

        for item in items:
            link = item.get("link", "")
            title = item.get("title", "")

            if "goodreturns.in" in link:
                # Step 2: Extract price
                price_per_g = extract_price_from_goodreturns(link, carat)
                total_price = price_per_g * weight

                return f"{weight}g of {carat}ct {metal.title()}: ₹{total_price:,.2f}"


        return "No trusted pricing source (like goodreturns.in) found in top results."

    except Exception as e:
        return f"Error in gold_search: {str(e)}"


# LangChain Tool wrapper
gold_search_tool = Tool.from_function(
    func=gold_search,
    name="gold_price_search",
    description=(
        "Fetch current pricing of metals like gold, silver, platinum, etc., using real-time search. "
        "Query format examples: '8g 22ct gold price', '100g 6ct gold rate today', 'silver rate today 10g'."
    )
)

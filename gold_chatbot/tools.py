# import os
# import re
# import requests
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv
# from langchain.tools import Tool

# load_dotenv()

# VALID_CARATS = [24, 22, 20, 18, 14, 10, 6]
# SUPPORTED_WEIGHTS = [1, 10, 100, 1000]

# # ------------------- GOLD ------------------- #
# def extract_gold_price_bullions(karat: str, weight_grams: int) -> str:
#     print(f"[DEBUG] extract_gold_price_bullions called with karat='{karat}', weight_grams={weight_grams}")
#     try:
#         url = "https://bullions.co.in/"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers, timeout=10)
#         print(f"[DEBUG] Fetched gold prices page with status code: {response.status_code}")
#         soup = BeautifulSoup(response.text, "html.parser")

#         table = soup.find("table", class_="data")
#         if not table:
#             print("[ERROR] Gold price table not found on the page.")
#             return "Gold price table not found on the site."
#         rows = table.find("tbody").find_all("tr")
#         print(f"[DEBUG] Found {len(rows)} rows in gold price table.")

#         karat_norm = karat.strip().lower().replace("kt", "karat").replace("ct", "karat")
#         # print(f"[DEBUG] Normalized karat for matching: '{karat_norm}'")

#         for row in rows:
#             cols = row.find_all("td")
#             if not cols:
#                 continue
#             karat_name = cols[0].text.strip().lower()
#             print(f"[DEBUG] Checking row karat name: '{karat_name}'")
#             if karat_norm in karat_name:
#                 price = cols[[1, 2, 3, 4][SUPPORTED_WEIGHTS.index(weight_grams)]].text.strip()
#                 print(f"[DEBUG] Matched karat '{karat_norm}'. Price found: {price}")
#                 return f"Price of {weight_grams}g {karat.title()} gold today is ₹{price}."
#         print(f"[DEBUG] Karat '{karat}' not found in gold price table.")
#         return f"{karat.title()} gold not found on the site."
#     except Exception as e:
#         print(f"[ERROR] Exception in extract_gold_price_bullions: {e}")
#         return f"Error fetching gold price: {str(e)}"

# # ------------------- SILVER ------------------- #
# def extract_silver_price(weight_grams: int, purity: str = "999") -> str:
#     # print(f"[DEBUG] extract_silver_price called with weight={weight_grams} purity={purity}")

#     valid_purities = get_available_silver_purities_from_site()
#     # print(f"[DEBUG] Valid silver purities retrieved: {valid_purities}")
#     if purity not in valid_purities:
#         # print(f"[DEBUG] Purity '{purity}' not in valid purities list.")
#         return (
#             f"Sorry, silver purity '{purity}' is not supported. "
#             f"Please ask for silver with purity {', '.join(valid_purities)}."
#         )

#     try:
#         url = "https://bullions.co.in/"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers, timeout=10)
#         # print(f"[DEBUG] Fetched silver prices page with status code: {response.status_code}")
#         soup = BeautifulSoup(response.text, "html.parser")

#         tables = soup.find_all("table", class_="data")
#         if len(tables) < 2:
#             print("[ERROR] Silver pricing table not found on the site.")
#             return "Silver pricing table not found on the site."

#         silver_table = tables[1]
#         rows = silver_table.find("tbody").find_all("tr")
#         # print(f"[DEBUG] Found {len(rows)} rows in silver price table.")

#         # Regex to flexibly match purity in string
#         pattern = re.compile(rf"silver\s*{purity}(\b|[^0-9])", re.IGNORECASE)

#         for row in rows:
#             cols = row.find_all("td")
#             if not cols:
#                 continue
#             purity_name = cols[0].text.strip()
#             # print(f"[DEBUG] Checking silver purity row: '{purity_name}' against purity: '{purity}'")
#             if pattern.search(purity_name):
#                 prices = [cols[i].text.strip() for i in range(1, 5)]
#                 # print(f"[DEBUG] Prices found for purity {purity}: {prices}")
#                 if weight_grams == 1:
#                     price = cols[1].text.strip()
#                 elif weight_grams == 10:
#                     price = cols[2].text.strip()
#                 elif weight_grams == 100:
#                     price = cols[3].text.strip()
#                 elif weight_grams == 1000:
#                     price = cols[4].text.strip()
#                 else:
#                     # print(f"[DEBUG] Unsupported weight requested: {weight_grams}g")
#                     return f"Unsupported weight: {weight_grams}g. Try 1g, 10g, 100g, or 1000g."

#                 # print(f"[DEBUG] Returning price for silver purity {purity}: {price}")
#                 return f"Price of {weight_grams}g Silver ({purity} purity) today is ₹{price}."

#         # print(f"[DEBUG] No matching silver purity '{purity}' found in table rows.")
#         return f"No matching silver purity ({purity}) found."

#     except Exception as e:
#         print(f"[ERROR] Exception in extract_silver_price: {e}")
#         return f"Error fetching silver price: {str(e)}"

# def get_available_silver_purities_from_site() -> list:
#     # print("[DEBUG] get_available_silver_purities_from_site called")
#     try:
#         url = "https://bullions.co.in/"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers, timeout=10)
#         # print(f"[DEBUG] Fetched page with status code: {response.status_code}")
#         soup = BeautifulSoup(response.text, "html.parser")

#         tables = soup.find_all("table", class_="data")
#         if len(tables) < 2:
#             print("[ERROR] Less than 2 tables found, cannot find silver pricing table.")
#             return []

#         rows = tables[1].find("tbody").find_all("tr")
#         # print(f"[DEBUG] Found {len(rows)} rows in silver pricing table.")

#         purities = []
#         for row in rows:
#             cols = row.find_all("td")
#             if not cols:
#                 continue
#             name = cols[0].text.strip().lower()
#             # print(f"[DEBUG] Checking row for purity extraction: '{name}'")
#             match = re.search(r'silver\s+(\d+)', name)
#             if match:
#                 purities.append(match.group(1))

#         # print(f"[DEBUG] Silver purities found on site: {purities}")
#         return purities
#     except Exception as e:
#         print(f"[ERROR] Exception in get_available_silver_purities_from_site: {e}")
#         return []

# # ------------------- MAIN TOOL ------------------- #
# def metal_search(query: str) -> str:
#     print(f"[TOOL INVOKED] metal_search() called with query: '{query}'")
#     try:
#         # Extract weight and convert kg to grams if needed
#         weight_match = re.search(r'(\d+(\.\d+)?)\s*(kg|kilogram|kilograms|g|gram|grams)', query.lower())
#         weight = 1
#         if weight_match:
#             weight_val = float(weight_match.group(1))
#             unit = weight_match.group(3)
#             weight = int(weight_val * 1000) if unit.startswith("kg") else int(weight_val)
#         print(f"[DEBUG] Extracted weight: {weight}g")

#         if weight not in SUPPORTED_WEIGHTS:
#             return f"Unsupported weight: {weight}g. Please use one of: {', '.join(map(str, SUPPORTED_WEIGHTS))}g."

#         # Extract metal type
#         metal_match = re.search(r'(gold|silver|platinum|palladium)', query.lower())
#         metal = metal_match.group(1).lower() if metal_match else "gold"
#         print(f"[DEBUG] Extracted metal: '{metal}'")

#         # ---- GOLD SECTION ----
#         if metal == "gold":
#             purity_or_carat = None
#             # Try to extract carat number BEFORE "gold", e.g. "18 Karat gold"
#             carat_match = re.search(r'(\d+)\s*(ct|karat|kt|purity)?\s*gold', query.lower())
#             if carat_match:
#                 purity_or_carat = carat_match.group(1)
#             else:
#                 # fallback: number after "gold" or anywhere with ct/karat suffix
#                 carat_match = re.search(r'(\d+)\s*(ct|karat|kt|purity)', query.lower())
#                 if carat_match:
#                     purity_or_carat = carat_match.group(1)
#             print(f"[DEBUG] Extracted purity_or_carat for gold: '{purity_or_carat}'")

#             if not purity_or_carat:
#                 return f"Please specify a carat value for gold (e.g., 24, 22, 18)."
#             if int(purity_or_carat) not in VALID_CARATS:
#                 return f"Unsupported gold carat: {purity_or_carat}. Valid options: {', '.join(map(str, VALID_CARATS))}."
#             return extract_gold_price_bullions(purity_or_carat, weight)

#         # ---- SILVER SECTION ----
#         elif metal == "silver":
#             purity_or_carat = None
#             metal_purity_match = re.search(rf'{metal}.*?(\d+)', query.lower())
#             if metal_purity_match:
#                 purity_or_carat = metal_purity_match.group(1)
#             # print(f"[DEBUG] Extracted purity_or_carat for silver: '{purity_or_carat}'")

#             available_purities = get_available_silver_purities_from_site()
#             # print(f"[DEBUG] Available purities: {available_purities}")

#             if not purity_or_carat:
#                 return f"Please specify a purity value for silver (e.g., {', '.join(available_purities)})."
#             if purity_or_carat not in available_purities:
#                 return f"Invalid silver purity: {purity_or_carat}. Try one of: {', '.join(available_purities)}."
#             # print(f"[DEBUG] Calling extract_silver_price with weight={weight} purity={purity_or_carat}")
#             return extract_silver_price(weight, purity_or_carat)

#         # ---- OTHER METALS ----
#         else:
#             return f"Currently I support only gold and silver rates."

#     except Exception as e:
#         print(f"[ERROR] Exception in metal_search: {e}")
#         return f"[ERROR] {str(e)}"

# # ------------------- LANGCHAIN TOOL ------------------- #
# gold_search_tool = Tool.from_function(
#     func=metal_search,
#     name="gold_price_search",
#     description=(
#         "Use this tool ONLY when the user asks for prices of gold or silver. "
#         "Examples: 'gold price today', '22 carat gold rate 10g', 'silver 999 100 grams price', "
#         "'price of 1 kilogram of Silver 800'."
#     )
# )

#=======================   gemini api  ========================


# import os
# import requests
# from dotenv import load_dotenv
# from langchain.tools import tool
# from system_message import cred_system_kalyan_jewelers,prompt_metal
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# llm_metal=ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )



# @tool
# def gold_price_data(query: str) -> str:
#     """
#     Fetches gold or silver price data from the bullion website based on the user's query.
#     Returns a concise price string like:
#     "Today's price for 24kt gold is ₹7,215 per gram."
#     """
#     try:
#         url = "https://bullions.co.in/"
#         headers = {"User-Agent": "Mozilla/5.0"}
#         response = requests.get(url, headers=headers, timeout=10)
#         print(f"[DEBUG] Fetched HTML from {url} with status code: {response.status_code}")
        
#         html = response.text[:100000]  # limit for LLM
#         print(f"[DEBUG] HTML snippet (first 500 chars):\n{html[:500]}")

#         prompt = prompt_metal.format(query=query, html=html)
#         print(f"[DEBUG] Generated prompt for Gemini:\n{prompt[:500]}")  # Print first 500 chars

#         result = llm_metal.invoke(prompt)
#         print(f"[DEBUG] Gemini response content:\n{result.content}")

#         return result.content.strip()
    
#     except Exception as e:
#         print(f"[ERROR] Exception in gold_price_data: {e}")
#         return f"Error fetching price: {e}"

#========================  removes cache  =================================================

# import os
# import requests
# import time
# from dotenv import load_dotenv
# from langchain.tools import tool
# from system_message import prompt_metal
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# llm_metal = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )

# # Cache variables for bullion HTML
# _cached_html = None
# _cached_time = 0
# CACHE_TTL = 600  # seconds (10 minutes)


# def get_bullions_html():
#     global _cached_html, _cached_time
#     now = time.time()
#     if _cached_html and (now - _cached_time) < CACHE_TTL:
#         print("[DEBUG] Using cached bullion HTML")
#         return _cached_html

#     print("[DEBUG] Fetching new bullion HTML")
#     url = "https://bullions.co.in/"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     response = requests.get(url, headers=headers, timeout=10)
#     if response.status_code == 200:
#         _cached_html = response.text[:100000]  # truncate to limit tokens
#         _cached_time = now
#         print("[DEBUG] Successfully fetched bullion HTML")
#         return _cached_html
#     else:
#         raise Exception(f"Failed to fetch bullion site HTML, status code: {response.status_code}")


# @tool
# def gold_price_data(query: str) -> str:
#     """
#     Tool to extract raw gold/silver price data from the bullion site
#     based on the user's query (e.g., '24kt gold price', '10g silver').
#     """
#     try:
#         start = time.time()
#         html = get_bullions_html()
#         print(f"[DEBUG] Time to fetch HTML: {time.time() - start:.2f}s")

#         start = time.time()
#         prompt = prompt_metal.format(query=query, html=html)
#         print(f"[DEBUG] Time to prepare prompt: {time.time() - start:.2f}s")

#         start = time.time()
#         result = llm_metal.invoke(prompt)
#         print(f"[DEBUG] Gemini API call latency: {time.time() - start:.2f}s")

#         return result.content.strip()

#     except Exception as e:
#         return f"Error fetching price: {e}"

#===========================  create a html =====================================
import os
import json
import time
from dotenv import load_dotenv
from langchain.tools import tool
from system_message import prompt_metal
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm_metal = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

PRICES_JSON = "prices.json"

def get_cached_prices():
    if os.path.exists(PRICES_JSON):
        print("[DEBUG] Reading prices data from:", PRICES_JSON)
        with open(PRICES_JSON, "r", encoding="utf-8") as f:
            prices = json.load(f)
        return prices
    else:
        print("[ERROR] Cached prices file not found")
        raise FileNotFoundError(f"{PRICES_JSON} not found. Please run the scraper/parser script.")

@tool
def gold_price_data(query: str) -> str:
    """
    Fetches gold or silver price data from the cached prices.json based on the user's query.
    Returns a concise price string like:
    "Today's price for 24kt gold is ₹7,215 per gram."
    """

    try:
        start = time.time()
        prices = get_cached_prices()
        print(f"[DEBUG] Loaded cached prices in {time.time() - start:.2f}s")

        # Here you can decide how you want to build the prompt
        # For example, pass prices dict as JSON string to the LLM prompt:
        start = time.time()
        prompt = prompt_metal.format(query=query, prices=json.dumps(prices))
        print(f"[DEBUG] Prompt prepared in {time.time() - start:.2f}s")

        start = time.time()
        result = llm_metal.invoke(prompt)
        print(f"[DEBUG] Gemini API call latency: {time.time() - start:.2f}s")

        return result.content.strip()

    except Exception as e:
        return f"Error fetching price: {e}"

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

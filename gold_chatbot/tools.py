# import os
# from googleapiclient.discovery import build
# from langchain.tools import Tool
# from dotenv import load_dotenv
# from datetime import datetime

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

#         # Relax filtering: only exclude results if absolutely no items
#         # Instead of filtering, just sort or prioritize items containing some keywords
#         keywords = ["today", "live", "current", str(datetime.now().year)]

#         # Separate items containing keywords vs others
#         prioritized = []
#         others = []
#         for item in items:
#             snippet = item.get("snippet", "").lower()
#             title = item.get("title", "").lower()
#             if any(kw in snippet or kw in title for kw in keywords):
#                 prioritized.append(item)
#             else:
#                 others.append(item)

#         # If no prioritized items found, fall back to all items
#         filtered_items = prioritized if prioritized else items

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
#         "Use this tool to fetch the current gold price, "
#         "live gold rate, or jewellery-related information from the web. "
#         "Provide a clear query like 'gold price today' or '22 carat gold rate in India'."
#     )
# )

import os
from googleapiclient.discovery import build
from langchain.tools import Tool
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

def rewrite_query(query: str) -> str:
    """
    Rewrite the user query to add defaults:
    - If no carat info, add '22 carat'
    - If no location info, add 'India'
    """
    query_lower = query.lower()

    # Add carat info if missing
    if not re.search(r"\b(22|24|18|14)\s*(carat|ct|k)\b", query_lower):
        query += " 22 carat"

    # Add location if missing
    if not re.search(r"\b(india|mumbai|delhi|hyderabad|bangalore|chennai)\b", query_lower):
        query += " India"

    return query.strip()

def gold_search(query: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")

    if not api_key or not cx_id:
        return "Error: GOOGLE_API_KEY and/or GOOGLE_CX_ID not set in .env"

    query = rewrite_query(query)

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cx_id, num=5).execute()

        items = res.get("items", [])
        if not items:
            return f"No results found for: {query}"

        # Relax filtering: return all items without filtering to maximize results
        filtered_items = items

        # Format and return output
        output = []
        for item in filtered_items:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            output.append(f"🔹 {title}\n{snippet}\n📎 {link}")

        return "\n\n".join(output)

    except Exception as e:
        return f"Error using Google Search API: {str(e)}"

def tools_condition(messages):
    """
    Decide if the tool should be invoked.
    Trigger on any message mentioning gold price or rate keywords.
    """
    if not messages:
        return False
    last_message = messages[-1].content.lower()
    trigger_keywords = ["gold", "price", "rate", "today", "live", "carat", "gram"]
    return any(keyword in last_message for keyword in trigger_keywords)

gold_search_tool = Tool.from_function(
    func=gold_search,
    name="gold_price_search",
    description=(
        "Use this tool to fetch the current gold price, "
        "live gold rate, or jewellery-related information from the web. "
        "Provide a clear query like 'gold price today' or '22 carat gold rate in India'."
    )
)

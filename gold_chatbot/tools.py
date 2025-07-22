import os
from googleapiclient.discovery import build
from langchain.tools import Tool
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def gold_search(query: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")

    if not api_key or not cx_id:
        return "Error: GOOGLE_API_KEY and/or GOOGLE_CX_ID not set in .env"

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cx_id, num=5).execute()

        items = res.get("items", [])
        if not items:
            return f"No results found for: {query}"

        # Relax filtering: only exclude results if absolutely no items
        # Instead of filtering, just sort or prioritize items containing some keywords
        keywords = ["today", "live", "current", str(datetime.now().year)]

        # Separate items containing keywords vs others
        prioritized = []
        others = []
        for item in items:
            snippet = item.get("snippet", "").lower()
            title = item.get("title", "").lower()
            if any(kw in snippet or kw in title for kw in keywords):
                prioritized.append(item)
            else:
                others.append(item)

        # If no prioritized items found, fall back to all items
        filtered_items = prioritized if prioritized else items

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

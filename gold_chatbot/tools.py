import os
from googleapiclient.discovery import build
from langchain.tools import Tool
from dotenv import load_dotenv

load_dotenv()

def gold_search(query: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    cx_id = os.getenv("GOOGLE_CX_ID")

    if not api_key or not cx_id:
        return "Error: GOOGLE_API_KEY and/or GOOGLE_CX_ID not set in .env"

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cx_id, num=3).execute()

        items = res.get("items", [])
        if not items:
            return f"No results found for: {query}"

        output = []
        for item in items:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            output.append(f"🔹 {title}\n{snippet}\n📎 {link}")

        return "\n\n".join(output)

    except Exception as e:
        return f"Error using Google Search API: {str(e)}"

gold_search_tool = Tool.from_function(
    func=gold_search,
    name="gold_price_search",
    description=(
        "Use this tool to search any information related to gold, silver, diamonds, shop timings, schemes, etc., "
        "from trusted jewellery sites configured in the Google Custom Search (CSE). Example: "
        "'silver rate today', '22ct price', 'jewellery schemes kalyan', 'store timing kalyan jewellers', etc."
    ),
)

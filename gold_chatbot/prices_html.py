import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

def fetch_and_save_html():
    url = "https://bullions.co.in/"
    headers = {"User-Agent": "Mozilla/5.0"}
    filename = "bullions_cached.html"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"[{datetime.now()}] Saved bullion site HTML to {filename}")
            return html_content
        else:
            print(f"Failed to fetch HTML, status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching HTML: {e}")
    return None

def extract_all_price_tables(html):
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    
    # Filter for tables that include Gold or Silver
    filtered_tables = []
    for table in tables:
        text = table.get_text().lower()
        if "gold" in text or "silver" in text:
            filtered_tables.append(str(table))

    if filtered_tables:
        return "\n<hr/>\n".join(filtered_tables)  # Add separator for readability
    else:
        return html[:5000]

def parse_prices_from_html(html):
    """
    Parse the price tables HTML and return nested dict like:
    {
        "gold": {
            "24kt": {"1 gram": 9937, "10 gram": 99370, ...},
            ...
        },
        "silver": {
            "999 fine": {"1 gram": 116, "10 gram": 1156, ...},
            ...
        }
    }
    """
    soup = BeautifulSoup(html, "html.parser")
    prices = {}

    # These are the price keys matching columns in tables
    price_keys = ["1 gram", "10 gram", "100 gram", "1 kilogram", "1 ounce", "1 tola"]

    tables = soup.find_all("table")
    for table in tables:
        # Check if table has correct headers
        thead = table.find("thead")
        if not thead:
            continue
        header_cols = thead.find_all("th")
        header_texts = [th.get_text(strip=True).lower() for th in header_cols]

        # Check if price keys are present in header
        if not all(any(pk in ht for ht in header_texts) for pk in ["gram", "ounce", "tola"]):
            continue

        tbody = table.find("tbody")
        if not tbody:
            continue

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if not cols or len(cols) < 2:
                continue

            # First col is name like "Gold 24 Karat", "Silver 900 Coin"
            name_text = cols[0].get_text(" ", strip=True).lower()

            # Determine metal and purity
            metal = None
            purity = None
            if "gold" in name_text:
                metal = "gold"
                m = re.search(r"(\d+)\s*karat", name_text)
                purity = f"{m.group(1)}kt" if m else "unknown"
            elif "silver" in name_text:
                metal = "silver"
                # For silver, use descriptive text after "silver"
                purity = name_text.replace("silver", "").strip()
            else:
                continue  # Skip rows not gold or silver

            price_data = {}
            for i, key in enumerate(price_keys, start=1):
                if i >= len(cols):
                    price_data[key] = None
                    continue
                val_text = cols[i].get_text(strip=True).replace(",", "")
                try:
                    val = int(float(val_text))
                except Exception:
                    val = None
                price_data[key] = val

            if metal not in prices:
                prices[metal] = {}
            prices[metal][purity] = price_data

    return prices


import json

if __name__ == "__main__":
    html = fetch_and_save_html()
    if html:
        table_html = extract_all_price_tables(html)
        with open("price_table.html", "w", encoding="utf-8") as f:
            f.write(table_html)
        print(f"[{datetime.now()}] Extracted and saved all price tables to price_table.html")

        # Parse prices to dict
        prices = parse_prices_from_html(table_html)
        print(f"[{datetime.now()}] Parsed prices dict:")

        # Pretty print prices dict (optional)
        # import pprint
        # pprint.pprint(prices)

        # Save prices dict as JSON file for reuse
        with open("prices.json", "w", encoding="utf-8") as f:
            json.dump(prices, f, indent=2)
        print(f"[{datetime.now()}] Saved prices dict to prices.json")

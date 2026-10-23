import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "hu-HU,hu;q=0.9"
}

TARGET_SHOPS = {
    "pcx": "PCX",
    "ipon": "iPon",
    "mediamarkt": "MediaMarkt",
    "media markt": "MediaMarkt",
    "alza": "Alza",
    "aqua": "Aqua",
    "konzolvilág": "Konzolvilág",
    "konzolvilag": "Konzolvilág",
    "skynet": "Skynet",
    "komphone": "Komphone",
    "foramax": "Foramax",
    "computer imperium": "Computer Imperium",
    "computerimperium": "Computer Imperium",
}

def normalize_shop_name(raw_name: str) -> str | None:
    lowered = raw_name.lower().strip()
    for keyword, standard_name in TARGET_SHOPS.items():
        if keyword in lowered:
            return standard_name
    return None

def parse_price(price_text: str) -> int:
    cleaned = "".join(ch for ch in price_text if ch.isdigit())
    if not cleaned:
        raise ValueError(f"Nem található érvényes ár: {price_text}")
    return int(cleaned)

def detect_category(product_name: str) -> str:
    name_upper = product_name.upper()
    if any(k in name_upper for k in ["DDR4", "DDR5", "RAM", "DIMM", "FURY", "VENGEANCE"]):
        return "RAM"
    if any(k in name_upper for k in ["RYZEN", "INTEL", "CORE I", "PROCESSZOR"]):
        return "CPU"
    if any(k in name_upper for k in ["RTX", "GTX", "RADEON", "RX ", "GEFORCE"]):
        return "GPU"
    return "OTHER"

def parse_arukereso_html(html_content: str, url: str = "") -> dict:
    soup = BeautifulSoup(html_content, "html.parser")

    title_el = soup.find("h1")
    if not title_el:
        raise ValueError("Nem található a termék címe (h1) a HTML-ben")
    product_name = title_el.get_text(strip=True)

    offers = []
    offer_blocks = soup.select("div.optoffer, div.offer")

    for block in offer_blocks:
        shop_el = block.select_one(".shop-name, [itemprop='name'], img[alt]")
        price_el = block.select_one(".price, [itemprop='price'], .row-price")

        if not shop_el or not price_el:
            continue

        raw_shop = (
            shop_el.get("alt", "").strip()
            if shop_el.name == "img"
            else shop_el.get_text(strip=True)
        )

        standard_shop = normalize_shop_name(raw_shop)
        if not standard_shop:
            continue

        try:
            price = parse_price(price_el.get_text(strip=True))
            offers.append({"shop": standard_shop, "price": price})
        except ValueError:
            continue

    if not offers:
        raise ValueError("Nem található ajánlat a 10 kijelölt bolt egyikétől sem")

    offers.sort(key=lambda x: x["price"])
    cheapest = offers[0]

    return {
        "name": product_name,
        "category": detect_category(product_name),
        "url": url,
        "best_price": cheapest["price"],
        "best_shop": cheapest["shop"],
        "offers": offers
    }

def fetch_arukereso_product(url: str, delay_seconds: float = 3.5) -> dict:
    time.sleep(delay_seconds)
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return parse_arukereso_html(response.text, url=url)
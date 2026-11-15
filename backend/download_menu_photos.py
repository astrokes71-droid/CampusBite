import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from sqlalchemy import select
from app.database import SessionLocal
from app.models import MenuItem

OUTPUT = Path("../frontend/public/food-images")
OUTPUT.mkdir(parents=True, exist_ok=True)

API = "https://commons.wikimedia.org/w/api.php"

HEADERS = {
    "User-Agent": "CampusBiteEducationalProject/1.0 (student food menu project)"
}

SEARCH_ALIASES = {
    "Veg Burger": "vegetarian burger",
    "Paneer Sandwich": "paneer sandwich",
    "Cheesy Pizza": "cheese pizza",
    "White Sauce Pasta": "alfredo pasta",
    "Veg Momos": "vegetable momo dumplings",
    "Masala Maggi": "instant noodles masala",
    "Peri Peri Fries": "seasoned french fries",
    "Veg Hakka Noodles": "vegetable hakka noodles",
    "Manchurian Dry": "vegetable manchurian",
    "Oreo Frappe": "oreo milkshake",
    "KitKat Shake": "chocolate milkshake",
    "Paneer Tikka Roll": "paneer kathi roll",
    "Aloo Tikki Burger": "potato burger",
    "Butter Maggi": "instant noodles",
    "Paneer Momos": "momo dumplings",
    "Fried Momos": "fried momos",
    "Schezwan Noodles": "schezwan noodles",
    "Schezwan Fried Rice": "spicy fried rice",
    "Chilli Paneer Gravy": "chilli paneer",
    "Honey Chilli Potato": "honey chilli potato",
    "Loaded Nachos with Cheese": "nachos cheese",
    "Corn & Cheese Pizza": "corn pizza",
    "Farmhouse Special Pizza": "vegetable pizza",
    "Mixed Sauce Pasta": "pink sauce pasta",
    "Cold Coffee with Ice Cream": "iced coffee ice cream",
    "Blue Lagoon Mocktail": "blue lagoon cocktail",
    "Green Apple Cooler": "green apple mocktail",
    "Waffle with Nutella": "chocolate waffle",
    "Pancakes with Maple Syrup": "pancakes maple syrup",
    "Vanilla Ice Cream Scoop": "vanilla ice cream",
    "Rajma Chawal": "rajma rice",
    "Dal Makhani with Rice": "dal makhani rice",
    "Rabri Jalebi": "jalebi rabri",
}

def slugify(value):
    return re.sub(
        r"[^a-z0-9]+", "-",
        value.lower()
    ).strip("-")

def search_image(query):
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": 6,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata",
        "iiurlwidth": 600,
        "format": "json",
    })

    request = urllib.request.Request(
        API + "?" + params,
        headers=HEADERS
    )

    with urllib.request.urlopen(
        request, timeout=25
    ) as response:
        data = json.load(response)

    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():
        info = page.get("imageinfo", [{}])[0]

        if info.get("mime") not in (
            "image/jpeg",
            "image/png"
        ):
            continue

        url = info.get("thumburl") or info.get("url")

        if url:
            return {
                "url": url,
                "source": info.get("descriptionurl", ""),
                "metadata": info.get("extmetadata", {}),
            }

    return None

with SessionLocal() as db:
    items = db.scalars(
        select(MenuItem).order_by(MenuItem.id)
    ).all()

print(f"Found {len(items)} menu items.")

mapping = {}
credits = {}

for index, item in enumerate(items, 1):
    name = item.name
    filename = slugify(name) + ".jpg"
    destination = OUTPUT / filename

    mapping[name] = f"/food-images/{filename}"

    if destination.exists():
        print(f"[{index}/{len(items)}] Exists: {name}")
        continue

    query = SEARCH_ALIASES.get(name, name)

    try:
        result = search_image(query)

        if not result:
            print(f"[{index}/{len(items)}] Missing: {name}")
            continue

        request = urllib.request.Request(
            result["url"],
            headers=HEADERS
        )

        with urllib.request.urlopen(
            request, timeout=30
        ) as response:
            image_data = response.read()

        from PIL import Image
        from io import BytesIO

        image = Image.open(BytesIO(image_data))
        image = image.convert("RGB")
        image.thumbnail((700, 700))
        image.save(destination, "JPEG", quality=85)

        credits[name] = {
            "source": result["source"],
            "metadata": result["metadata"]
        }

        print(f"[{index}/{len(items)}] Downloaded: {name}")

    except Exception as error:
        print(f"[{index}/{len(items)}] Failed: {name}: {error}")

    time.sleep(5)

Path("../frontend/src/foodImages.json").write_text(
    json.dumps(mapping, indent=2)
)

Path("../frontend/food-image-credits.json").write_text(
    json.dumps(credits, indent=2)
)

print("\nFinished downloading menu photos.")
print("Mapping created at frontend/src/foodImages.json")
print("Review downloaded images and their licenses before publishing.")

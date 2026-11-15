import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
OUTPUT = Path("public/food-images")
OUTPUT.mkdir(parents=True, exist_ok=True)

foods = {
    "Veg Burger": "vegetarian burger",
    "Paneer Sandwich": "paneer sandwich",
    "French Fries": "french fries",
    "Cold Coffee": "iced coffee",
    "Cheesy Pizza": "cheese pizza",
    "White Sauce Pasta": "alfredo pasta",
    "Veg Momos": "vegetable momos",
    "Garlic Bread": "garlic bread",
    "Masala Maggi": "maggi noodles",
    "Cheese Corn Sandwich": "corn cheese sandwich",
    "Peri Peri Fries": "peri peri fries",
    "Veg Hakka Noodles": "hakka noodles",
    "Manchurian Dry": "vegetable manchurian",
    "Chocolate Shake": "chocolate milkshake",
    "Masala Chai": "masala chai",
    "Samosa (2 pcs)": "samosa",
    "Gulab Jamun (2 pcs)": "gulab jamun",
}

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def get_image(query):
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": f'filetype:bitmap {query}',
        "gsrnamespace": 6,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": 600,
        "format": "json"
    })

    request = urllib.request.Request(
        API + "?" + params,
        headers={"User-Agent": "CampusBiteStudentProject/1.0 (educational project)"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)

    for page in data.get("query", {}).get("pages", {}).values():
        info = page.get("imageinfo", [{}])[0]
        if info.get("mime") in ("image/jpeg", "image/png"):
            return info.get("thumburl", info.get("url"))

    return None

for name, query in foods.items():
    destination = OUTPUT / (slugify(name) + ".jpg")

    try:
        url = get_image(query)
        if not url:
            print("No image found:", name)
            continue

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "CampusBiteStudentProject/1.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            image = response.read()

        destination.write_bytes(image)
        print("Downloaded:", name)

    except Exception as error:
        print("Failed:", name, error)

print("Image downloading finished.")

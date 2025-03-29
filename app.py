import threading
import webbrowser
from datetime import datetime, timedelta

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


def get_latest_arena_set():
    """Fetch the latest set with >200 cards and 90%+ Timeless legality on Arena."""

    # Get today's and tomorrow's date in YYYY-MM-DD format
    today = datetime.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Step 1: Fetch all sets
    url = "https://api.scryfall.com/sets"
    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        print("Error fetching sets from Scryfall.")
        return ""

    sets = response.json().get("data", [])

    # Step 2: Filter for Arena-relevant sets released before today
    valid_sets = [
        s
        for s in sets
        if s.get("released_at", tomorrow) <= today  # Exclude future sets
        and s.get("set_type", "").lower()
        in ["expansion", "core"]  # Only use specific set types
        and s.get("card_count", 0) > 200  # Ensure set has more than 200 cards
    ]

    # Step 3: Sort by release date (newest first) and take the last 10 sets
    latest_sets = sorted(
        valid_sets, key=lambda s: s.get("released_at", ""), reverse=True
    )[:10]

    # Step 4: Check Timeless legality for each set
    for s in latest_sets:
        set_code = s["code"]
        cards_url = (
            f"https://api.scryfall.com/cards/search?order=set&q=set%3A"
            f"{set_code}"
            f"&unique=prints"
        )
        cards_response = requests.get(cards_url, timeout=10)

        if cards_response.status_code != 200:
            print(f"Error fetching cards for set {set_code}.")
            continue

        cards = cards_response.json().get("data", [])

        # Step 5: Count cards that are legal in Timeless
        total_cards = len(cards)
        legal_cards = sum(
            1 for card in cards if card.get("legalities", {}).get("standard") == "legal"
        )

        # Step 6: Check if at least 90% of cards are legal in Standard
        if total_cards > 0 and (legal_cards / total_cards) >= 0.9:
            return set_code  # Return the first valid set

    return ""  # No matching set found


@app.route("/")
def index():
    return render_template("index.html", latest_set_code=latest_set_code)


@app.route("/fetch_cards", methods=["GET"])
def fetch_cards():
    # Get query parameters
    query = request.args.get("q", "Totally Lost")
    order = request.args.get("order", "cmc")
    direction = request.args.get("dir", "asc")

    # Query Scryfall API
    query_url = "https://api.scryfall.com/cards/search"
    params = {"q": query, "order": order, "dir": direction}
    response = requests.get(query_url, params=params, timeout=10)

    try:
        data = response.json()
    except Exception:
        return jsonify({"message": "", "cards": []})

    if "data" not in data or not data["data"]:
        return jsonify({"message": "", "cards": []})

    card_images = [
        card["image_uris"]["small"]
        for card in data["data"]
        if "image_uris" in card and "small" in card["image_uris"]
    ]

    if not card_images:
        return jsonify({"message": "", "cards": []})

    return jsonify({"cards": card_images})


if __name__ == "__main__":
    # Get the latest Standard-legal set code
    latest_set_code = get_latest_arena_set().upper()

    def open_browser():
        webbrowser.open("http://127.0.0.1:5000/")

    threading.Timer(1, open_browser).start()
    app.run()

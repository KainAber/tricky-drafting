import threading
import webbrowser

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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

    def open_browser():
        webbrowser.open("http://127.0.0.1:5000/")

    threading.Timer(1, open_browser).start()
    app.run()

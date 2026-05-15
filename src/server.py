"""
Vocab in News - Web Server (Iteration 0)
Minimal Flask app serving a single article reading page.
"""

import json
import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)

SAMPLE_ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "sample_article.json")


def load_article():
    with open(SAMPLE_ARTICLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    """Serve the main reading page."""
    article = load_article()
    return render_template("index.html", article=article)


@app.route("/api/article")
def api_article():
    """Return article as JSON."""
    article = load_article()
    return jsonify(article)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)

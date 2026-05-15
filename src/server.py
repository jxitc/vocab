"""
Vocab in News - Web Server (Iteration 1)
Flask app serving interactive article reading page with
word annotation and paragraph-level Chinese translations.
"""

import json
import os

from flask import Flask, jsonify, render_template

from vocab_service import find_difficult_words, tokenize

app = Flask(__name__)

SAMPLE_ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "sample_article.json")


def load_article():
    with open(SAMPLE_ARTICLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_paragraphs_with_tokens(article: dict) -> list:
    """Process article paragraphs, adding tokenization and difficult-word data."""
    enriched = []
    for para in article.get("paragraphs", []):
        text = para["text"]
        tokens = tokenize(text)
        difficult_words = find_difficult_words(text)
        enriched.append({
            "text": text,
            "translation": para["translation"],
            "tokens": tokens,
            "difficult_words": difficult_words,
        })
    return enriched


@app.route("/")
def index():
    """Serve the main reading page."""
    article = load_article()
    paragraphs = build_paragraphs_with_tokens(article)
    return render_template("index.html", article=article, paragraphs=paragraphs)


@app.route("/api/article")
def api_article():
    """Return article as JSON with vocabulary annotations."""
    article = load_article()
    paragraphs = build_paragraphs_with_tokens(article)
    return jsonify({
        "title": article["title"],
        "source": article["source"],
        "url": article.get("url", ""),
        "date": article["date"],
        "paragraphs": paragraphs,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)

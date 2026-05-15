"""
Vocab in News - Web Server (Iteration 1)
Flask app serving interactive article reading page with
word annotation and paragraph-level Chinese translations.
"""

import json
import os

from flask import Flask, jsonify, render_template

from vocab_service import find_difficult_words, find_difficult_words_sorted, tokenize

app = Flask(__name__)

SAMPLE_ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "sample_article.json")


def load_article():
    with open(SAMPLE_ARTICLE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


MAX_HIGHLIGHT_WORDS = 6  # Limit highlighted words per article for learners

def build_paragraphs_with_tokens(article: dict) -> list:
    """Process article paragraphs, adding tokenization and difficult-word data.

    Limits highlighted words to MAX_HIGHLIGHT_WORDS to avoid overwhelming
    learners (user research says 3-5 optimal, 8+ causes dropout).
    """
    # Collect all difficult words across the whole article, sorted by first appearance
    full_text = " ".join(p["text"] for p in article.get("paragraphs", []))
    all_difficult = find_difficult_words_sorted(full_text)
    # Only highlight the first N words; rest are shown as normal
    highlighted_lowers = {w["lower"] for w in all_difficult[:MAX_HIGHLIGHT_WORDS]}

    enriched = []
    for para in article.get("paragraphs", []):
        text = para["text"]
        tokens = tokenize(text)
        # Downgrade words that exceed the highlight limit
        for t in tokens:
            if t["is_difficult"] and t["word"] and t["word"].lower() not in highlighted_lowers:
                t["is_difficult"] = False
        difficult_words = [w for w in find_difficult_words(text)
                          if w["lower"] in highlighted_lowers]
        enriched.append({
            "text": text,
            "translation": para["translation"],
            "tokens": tokens,
            "difficult_words": difficult_words,
        })
    return enriched


@app.route("/")
def index():
    """Serve the main reading page shell (client-side rendering fetches /api/article)."""
    return render_template("index.html")


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

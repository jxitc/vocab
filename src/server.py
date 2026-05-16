"""
Vocab in News - Web Server (Iteration 18)
Flask app serving interactive article reading page with
word annotation, paragraph-level Chinese translations,
multiple difficulty levels, and multiple articles.
"""

import json
import os

from flask import Flask, jsonify, render_template, request

from vocab_service import (
    find_difficult_words,
    find_difficult_words_sorted,
    tokenize,
    get_levels_for_user,
    get_max_highlights,
    filter_known_words,
    filter_known_words_from_tokens,
    stem_word,
    LEVEL_NAMES,
)


app = Flask(__name__)

SAMPLE_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "sample_articles.json")


def load_articles():
    """Load all articles from the JSON array file."""
    with open(SAMPLE_ARTICLES_PATH, "r", encoding="utf-8") as f:
        articles = json.load(f)
    return articles


def get_article_by_id(article_id: int):
    """Load a specific article by id. Returns None if not found."""
    articles = load_articles()
    for a in articles:
        if a.get("id") == article_id:
            return a
    return None


def build_paragraphs_with_tokens(article: dict, user_level: int = 2,
                                  known_words: set = None) -> list:
    """Process article paragraphs, adding tokenization and difficult-word data.

    Limits highlighted words based on level-specific MAX_HIGHLIGHTS.
    Excludes words in known_words set from being highlighted.
    """
    if known_words is None:
        known_words = set()

    max_highlights = get_max_highlights(user_level)

    # Collect all difficult words across the whole article, sorted by first appearance
    full_text = " ".join(p["text"] for p in article.get("paragraphs", []))
    all_difficult = find_difficult_words_sorted(full_text, user_level)

    # Exclude known words from difficult list
    all_difficult = filter_known_words(all_difficult, known_words)

    # Only highlight the first N words; rest are shown as normal
    highlighted_lowers = {w["lower"] for w in all_difficult[:max_highlights]}

    # Track first occurrence by stem — group inflectional variants
    seen_stems = set()

    enriched = []
    for para in article.get("paragraphs", []):
        text = para["text"]
        tokens = tokenize(text, user_level)
        # Clear known words from token difficulty flags
        tokens = filter_known_words_from_tokens(tokens, known_words)
        # Downgrade words that exceed the highlight limit or are repeat stem occurrences
        for t in tokens:
            if t["is_difficult"] and t["word"]:
                wl = t["word"].lower()
                if wl not in highlighted_lowers:
                    t["is_difficult"] = False
                else:
                    ws = stem_word(wl)
                    if ws in seen_stems:
                        t["is_difficult"] = False
                    else:
                        seen_stems.add(ws)
        difficult_words = [w for w in find_difficult_words(text, user_level)
                          if w["lower"] in highlighted_lowers]
        difficult_words = filter_known_words(difficult_words, known_words)
        enriched.append({
            "text": text,
            "translation": para["translation"],
            "tokens": tokens,
            "difficult_words": difficult_words,
        })
    return enriched


@app.route("/")
def index():
    """Serve the main reading page shell."""
    return render_template("index.html")


@app.route("/api/articles")
def api_articles():
    """Return list of article summaries (title, source, date, id)."""
    articles = load_articles()
    summaries = []
    for a in articles:
        summaries.append({
            "id": a.get("id", 0),
            "title": a.get("title", ""),
            "source": a.get("source", ""),
            "date": a.get("date", ""),
        })
    return jsonify(summaries)


@app.route("/api/article")
def api_article():
    """Return article as JSON with vocabulary annotations.

    Query params:
        id: article id (default 0)
        level: user difficulty level 1-4 (default 2 = 初中)
    """
    article_id = request.args.get("id", 0, type=int)
    user_level = request.args.get("level", 2, type=int)

    # Clamp level to valid range
    if user_level < 1:
        user_level = 1
    elif user_level > 4:
        user_level = 4

    # Known words filtering (client sends comma-separated lowercase words)
    known_raw = request.args.get("known", "")
    known_words = set()
    if known_raw:
        known_words = {w.strip().lower() for w in known_raw.split(",") if w.strip()}

    article = get_article_by_id(article_id)
    if article is None:
        # Fall back to first article
        articles = load_articles()
        if articles:
            article = articles[0]
        else:
            return jsonify({"error": "No articles found"}), 404

    paragraphs = build_paragraphs_with_tokens(article, user_level, known_words)

    return jsonify({
        "id": article.get("id", 0),
        "title": article["title"],
        "source": article["source"],
        "url": article.get("url", ""),
        "date": article["date"],
        "level": user_level,
        "levelName": LEVEL_NAMES.get(user_level, "初中"),
        "maxHighlights": get_max_highlights(user_level),
        "paragraphs": paragraphs,
    })


@app.route("/api/levels")
def api_levels():
    """Return level configuration for the frontend."""
    return jsonify({
        "levels": [
            {"id": 1, "name": "小学", "maxHighlights": 3},
            {"id": 2, "name": "初中", "maxHighlights": 6},
            {"id": 3, "name": "高中", "maxHighlights": 8},
            {"id": 4, "name": "大学", "maxHighlights": 10},
        ],
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)

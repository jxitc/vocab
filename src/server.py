"""
Vocab in News - MVP Web Server
Flask app serving interactive article reading with word annotation,
user word bank, and quizzes.  Hardcoded to user_level=2 (初中).
"""

import json
import os
import random
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, render_template, request, session

from vocab_service import (
    _lookup,
    VOCAB_DIFFICULTY,
    filter_known_words,
    filter_known_words_from_tokens,
    find_difficult_words,
    find_difficult_words_sorted,
    get_levels_for_user,
    get_max_highlights,
    stem_word,
    tokenize,
    LEVEL_NAMES,
)
from wordlist import (
    list_wordlists,
    load_wordlist,
    get_pending_words,
    pick_words_to_inject,
    mark_words_injected,
    load_progress as wl_load_progress,
)

# ── App setup ──────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "vocab-in-news-mvp-dev-secret-key"

SAMPLE_ARTICLES_PATH = os.path.join(os.path.dirname(__file__), "sample_articles.json")
DATA_DIR = Path(__file__).parent / "data" / "users"

MVP_USER_LEVEL = 2  # 初中 — hardcoded for MVP

# Per-user thread locks to serialise JSON file writes safely
_locks: dict = {}
_lock_registry = threading.Lock()


def _get_user_lock(username: str) -> threading.Lock:
    """Return or create a per-user Lock for safe concurrent writes."""
    with _lock_registry:
        if username not in _locks:
            _locks[username] = threading.Lock()
        return _locks[username]


# ── Filesystem helpers ─────────────────────────────────────────────────

def _user_dir(username: str) -> Path:
    return DATA_DIR / username


def _ensure_user_dir(username: str) -> Path:
    d = _user_dir(username)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_json(username: str, filename: str, default=None):
    """Load JSON from a per-user file; return *default* if missing."""
    path = _user_dir(username) / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}


def _save_json(username: str, filename: str, data) -> None:
    """Atomically save JSON to a per-user file."""
    _ensure_user_dir(username)
    path = _user_dir(username) / filename
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _get_username() -> Optional[str]:
    """Return the current session username, or None."""
    return session.get("username")


def _require_user():
    """Return username or abort with a JSON error."""
    user = _get_username()
    if not user:
        return None
    return user


# ── Article helpers (kept from previous iteration) ─────────────────────

def load_articles() -> list:
    """Load all articles from the JSON array file."""
    with open(SAMPLE_ARTICLES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_article_by_id(article_id: int) -> Optional[dict]:
    """Load a specific article by id.  Returns None if not found."""
    for a in load_articles():
        if a.get("id") == article_id:
            return a
    return None


def build_paragraphs_with_tokens(article: dict,
                                 known_words: Optional[set] = None) -> list:
    """Process article paragraphs: tokenise + flag difficult words.

    Hardcodes user_level = 2 (初中).  Excludes words in *known_words* from
    being highlighted and limits highlights per MAX_HIGHLIGHTS for the level.
    """
    if known_words is None:
        known_words = set()

    max_highlights = get_max_highlights(MVP_USER_LEVEL)

    full_text = " ".join(p["text"] for p in article.get("paragraphs", []))
    all_difficult = find_difficult_words_sorted(full_text, MVP_USER_LEVEL)
    all_difficult = filter_known_words(all_difficult, known_words)

    highlighted_lowers = {w["lower"] for w in all_difficult[:max_highlights]}
    seen_stems: set = set()

    enriched = []
    for para in article.get("paragraphs", []):
        text = para["text"]
        tokens = tokenize(text, MVP_USER_LEVEL)
        tokens = filter_known_words_from_tokens(tokens, known_words)
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
        difficult_words = [
            w for w in find_difficult_words(text, MVP_USER_LEVEL)
            if w["lower"] in highlighted_lowers
        ]
        difficult_words = filter_known_words(difficult_words, known_words)
        enriched.append({
            "text": text,
            "translation": para["translation"],
            "tokens": tokens,
            "difficult_words": difficult_words,
        })
    return enriched


# ── User bootstrap (before first request) ──────────────────────────────

@app.before_request
def _capture_user():
    """Sniff ?user=xxx and store in session when not already logged in."""
    if "username" not in session:
        user = (request.args.get("user") or "").strip()
        if user:
            session["username"] = user
            _ensure_user_dir(user)
            if not (_user_dir(user) / "profile.json").exists():
                _save_json(user, "profile.json", {
                    "username": user,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
            # Initialise empty word bank if missing
            if not (_user_dir(user) / "words.json").exists():
                _save_json(user, "words.json", {
                    "learned": {},
                    "known": {},
                })


# ═══════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Reading page — supports ?article_id=N to read a specific article."""
    return render_template("index.html")


@app.route("/home")
def home():
    """Dashboard page."""
    return render_template("home.html")


@app.route("/wordlist")
def wordlist_page():
    """Word list management page."""
    return render_template("wordlist.html")


@app.route("/words")
def words_page():
    """Word bank page."""
    return render_template("words.html")


@app.route("/quiz")
def quiz_page():
    """Quiz page."""
    return render_template("quiz.html")


# ═══════════════════════════════════════════════════════════════════════
# API — Session
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/login", methods=["POST"])
def api_login():
    """Set username in session from JSON body."""
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username required"}), 400
    session["username"] = username
    _ensure_user_dir(username)
    if not (_user_dir(username) / "profile.json").exists():
        _save_json(username, "profile.json", {
            "username": username,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    if not (_user_dir(username) / "words.json").exists():
        _save_json(username, "words.json", {"learned": {}, "known": {}})
    return jsonify({"user": username})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """Clear the session."""
    session.pop("username", None)
    return jsonify({"ok": True})


@app.route("/api/session")
def api_session():
    """Return current user info, or null if not logged in."""
    user = _get_username()
    if not user:
        return jsonify({"user": None})
    return jsonify({"user": user})


# ═══════════════════════════════════════════════════════════════════════
# API — Daily Article  (GET /api/today)
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/today")
def api_today():
    """Return a single article.  Defaults to day-of-year mod N.

    Query: ?article_id=N  to request a specific article.
    Hardcodes user_level=2.  If a user is logged in, known words are
    loaded from their word bank and excluded from highlights.
    """
    articles = load_articles()
    if not articles:
        return jsonify({"error": "No articles found"}), 404

    article_id = request.args.get("article_id", type=int)
    if article_id is None:
        day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
        article_id = day_of_year % len(articles)

    article = get_article_by_id(article_id)
    if not article:
        article = articles[article_id % len(articles)]  # fallback

    # Load known words for logged-in user
    known_words: set = set()
    user = _get_username()
    if user:
        wb = _load_json(user, "words.json", {"learned": {}, "known": {}})
        known_words = set(wb.get("learned", {}).keys()) | set(wb.get("known", {}).keys())

    paragraphs = build_paragraphs_with_tokens(article, known_words)

    return jsonify({
        "id": article.get("id", article_id),
        "title": article["title"],
        "source": article["source"],
        "url": article.get("url", ""),
        "date": article["date"],
        "level": MVP_USER_LEVEL,
        "levelName": LEVEL_NAMES.get(MVP_USER_LEVEL, "初中"),
        "maxHighlights": get_max_highlights(MVP_USER_LEVEL),
        "paragraphs": paragraphs,
        "comprehension": article.get("comprehension", []),
        "topic": article.get("topic", ""),
    })


# ═══════════════════════════════════════════════════════════════════════
# API — Any-Word Lookup  (GET /api/lookup?word=xxx)
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/lookup")
def api_lookup():
    """Look up *any* English word.  Returns {definition, pos, level} or null.

    Uses the vocab database with stemming fallback, so inflectional
    forms (e.g. "discoveries") match their base entries.
    """
    word = (request.args.get("word") or "").strip().lower()
    if not word or not word.isascii():
        return jsonify(None)

    entry = _lookup(word)
    if entry is None:
        return jsonify({"found": False})

    definition, pos, level = entry
    return jsonify({
        "found": True,
        "word": word,
        "definition": definition,
        "pos": pos,
        "level": level,
        "levelName": LEVEL_NAMES.get(level, ""),
    })


# ═══════════════════════════════════════════════════════════════════════
# API — Word Bank  (per user)
# ═══════════════════════════════════════════════════════════════════════

def _load_wordbank(username: str) -> dict:
    """Load or create words.json for a user."""
    default = {"learned": {}, "known": {}}
    return _load_json(username, "words.json", default)


@app.route("/api/words")
def api_words():
    """Return the user's full word bank (learned + known lists)."""
    user = _require_user()
    if not user:
        return jsonify(None)
    wb = _load_wordbank(user)
    return jsonify({
        "learned": [{"word": w, **info} for w, info in wb.get("learned", {}).items()],
        "known": [{"word": w, **info} for w, info in wb.get("known", {}).items()],
    })


@app.route("/api/words/learn", methods=["POST"])
def api_words_learn():
    """Mark a word as learned.

    Body:  {"word": "...", "definition": "..."}
    The server fills in pos/level from the vocab database (or null).
    """
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    body = request.get_json(silent=True) or {}
    word = (body.get("word") or "").strip()
    definition = (body.get("definition") or "").strip()
    if not word:
        return jsonify({"error": "word is required"}), 400

    lock = _get_user_lock(user)
    with lock:
        wb = _load_wordbank(user)
        wb.setdefault("learned", {})
        wb.setdefault("known", {})

        # Pull pos & level from vocab if available
        entry = _lookup(word.lower())
        pos, level = (entry[1], entry[2]) if entry else (None, None)

        wb["learned"][word] = {
            "definition": definition,
            "pos": pos,
            "level": level,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        # Remove from known if present
        wb["known"].pop(word, None)

        _save_json(user, "words.json", wb)

    return jsonify({"ok": True, "word": word, "bank": wb})


@app.route("/api/words/known", methods=["POST"])
def api_words_known():
    """Mark a word as known (no definition needed).

    Body:  {"word": "..."}
    """
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    body = request.get_json(silent=True) or {}
    word = (body.get("word") or "").strip()
    if not word:
        return jsonify({"error": "word is required"}), 400

    lock = _get_user_lock(user)
    with lock:
        wb = _load_wordbank(user)
        wb.setdefault("learned", {})
        wb.setdefault("known", {})

        wb["known"][word] = {
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        # Remove from learned if present
        wb["learned"].pop(word, None)

        _save_json(user, "words.json", wb)

    return jsonify({"ok": True, "word": word, "bank": wb})


@app.route("/api/words/remove", methods=["POST"])
def api_words_remove():
    """Remove a word from both learned and known lists.

    Body:  {"word": "..."}
    """
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    body = request.get_json(silent=True) or {}
    word = (body.get("word") or "").strip()
    if not word:
        return jsonify({"error": "word is required"}), 400

    lock = _get_user_lock(user)
    with lock:
        wb = _load_wordbank(user)
        wb.setdefault("learned", {})
        wb.setdefault("known", {})

        wb["learned"].pop(word, None)
        wb["known"].pop(word, None)

        _save_json(user, "words.json", wb)

    return jsonify({"ok": True, "word": word, "bank": wb})


# ═══════════════════════════════════════════════════════════════════════
# API — Quiz  (per user, per article)
# ═══════════════════════════════════════════════════════════════════════

def _build_quiz(article: dict) -> dict:
    """Generate quiz questions for a single article.

    Returns a dict with two keys:
      - choice_questions (vocabulary choice, up to 5)
      - tf_questions (comprehension T/F, up to 5)
    """
    choice_questions = []
    tf_questions = []

    # ── Vocabulary choice questions ────────────────────────────────
    full_text = " ".join(p["text"] for p in article.get("paragraphs", []))
    difficult = find_difficult_words_sorted(full_text, MVP_USER_LEVEL)

    # Build a bank of all definitions for distractors
    all_defs = [(w, entry[0]) for w, entry in VOCAB_DIFFICULTY.items()]

    vocab_pool = difficult[:5]  # up to 5 vocab questions
    for item in vocab_pool:
        correct_word = item["word"]
        correct_def = item["definition"]
        # Pick 3 random wrong definitions (exclude the correct one)
        others = [d for w, d in all_defs if d != correct_def]
        if len(others) < 3:
            continue  # not enough distractors; skip
        wrongs = random.sample(others, 3)
        options = wrongs + [correct_def]
        random.shuffle(options)

        choice_questions.append({
            "type": "choice",
            "question": f"What does \"{correct_word}\" mean?",
            "word": correct_word,
            "options": options,
            "correct": correct_def,
        })

    # ── Comprehension T/F questions ────────────────────────────────
    comp = article.get("comprehension", [])
    for item in comp[:5]:  # up to 5 comprehension questions
        tf_questions.append({
            "type": "tf",
            "question": item.get("question", ""),
            "answer": item.get("answer", False),
        })

    return {
        "choice_questions": choice_questions,
        "tf_questions": tf_questions,
    }


@app.route("/api/quiz")
def api_quiz():
    """Generate quiz for an article.

    Query:  ?article_id=N  (defaults to today's article when omitted or 0)
    Returns:  {article_id, choice_questions: [...], tf_questions: [...]}
    """
    article_id = request.args.get("article_id", type=int)

    # Default to today's article when article_id not provided
    if article_id is None:
        articles = load_articles()
        if articles:
            day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
            article_id = day_of_year % len(articles)

    article = get_article_by_id(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    quiz = _build_quiz(article)

    return jsonify({
        "article_id": article.get("id", article_id),
        "choice_questions": quiz["choice_questions"],
        "tf_questions": quiz["tf_questions"],
    })


@app.route("/api/quiz/result", methods=["POST"])
def api_quiz_result():
    """Save a quiz result.

    Body:  {"article_id": N, "score": N, "total": N, "answers": [...]}
    """
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    body = request.get_json(silent=True) or {}
    article_id = body.get("article_id", 0)
    score = body.get("score", 0)
    total = body.get("total", 0)
    answers = body.get("answers", [])

    record = {
        "article_id": article_id,
        "score": score,
        "total": total,
        "date": datetime.now(timezone.utc).isoformat(),
        "answers": answers,
    }

    lock = _get_user_lock(user)
    with lock:
        results = _load_json(user, "quiz_results.json", [])
        results.append(record)
        _save_json(user, "quiz_results.json", results)

    return jsonify({"ok": True, "record": record})


@app.route("/api/read/done", methods=["POST"])
def api_read_done():
    """Mark an article as read (\"我读完了\" button).

    Body:  {"article_id": N}
    Saves to read_log.json.
    """
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    body = request.get_json(silent=True) or {}
    article_id = body.get("article_id", 0)

    record = {
        "article_id": article_id,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }

    lock = _get_user_lock(user)
    with lock:
        log = _load_json(user, "read_log.json", [])
        log.append(record)
        _save_json(user, "read_log.json", log)

    return jsonify({"ok": True, "record": record})


@app.route("/api/articles")
def api_articles():
    """Return summaries for all articles (title, source, date, id, wordCount, topic)."""
    articles = load_articles()
    summaries = []
    for a in articles:
        word_count = sum(len(p["text"].split()) for p in a.get("paragraphs", []))
        summaries.append({
            "id": a.get("id", 0),
            "title": a.get("title", ""),
            "source": a.get("source", ""),
            "date": a.get("date", ""),
            "wordCount": word_count,
            "topic": a.get("topic", ""),
        })
    return jsonify(summaries)


@app.route("/api/user/stats")
def api_user_stats():
    """Return reading stats for the logged-in user."""
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    read_log = _load_json(user, "read_log.json", [])
    wb = _load_json(user, "words.json", {"learned": {}, "known": {}})

    # Count unique articles read
    articles_read = len(read_log) if isinstance(read_log, list) else 0

    # Count learned words
    words_learned = len(wb.get("learned", {}))

    # Compute streak (consecutive days with reads)
    streak = 0
    if isinstance(read_log, list) and read_log:
        read_dates = set()
        for entry in read_log:
            try:
                ts = entry.get("finished_at", "")
                if ts:
                    d = ts[:10]
                    read_dates.add(d)
            except Exception:
                pass
        # Count backwards from today
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        check = datetime.now(timezone.utc)
        while True:
            ds = check.strftime("%Y-%m-%d")
            if ds in read_dates:
                streak += 1
                check = check.replace(day=check.day - 1)
            elif ds == today:
                check = check.replace(day=check.day - 1)
            else:
                break

    return jsonify({
        "articlesRead": articles_read,
        "wordsLearned": words_learned,
        "streak": streak,
    })


@app.route("/api/user/read-log")
def api_user_read_log():
    """Return the read log for the logged-in user."""
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify(_load_json(user, "read_log.json", []))


# ═══════════════════════════════════════════════════════════════════════
# API — Word Lists
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/wordlists")
def api_wordlists():
    """Return available word lists with user progress."""
    lists = list_wordlists()
    user = _get_username()
    progress = {}
    if user:
        p = wl_load_progress(user)
        for wl in lists:
            name = wl["name"]
            entry = p.get(name, {})
            progress[name] = {
                "injected": len(entry.get("injected", [])),
                "learned": len(entry.get("learned", [])),
            }
    return jsonify({"lists": lists, "progress": progress})


@app.route("/api/wordlist/<filename>")
def api_wordlist_detail(filename):
    """Return a specific word list with per-word status for current user."""
    wl = load_wordlist(filename)
    if not wl:
        return jsonify({"error": "Word list not found"}), 404

    user = _get_username()
    words = wl.get("words", [])

    # Attach status per word
    if user:
        p = wl_load_progress(user)
        entry = p.get(wl["name"], {})
        injected_set = set(entry.get("injected", []))
        learned_set = set(entry.get("learned", []))
        for w in words:
            if w["word"] in learned_set:
                w["status"] = "learned"
            elif w["word"] in injected_set:
                w["status"] = "injected"
            else:
                w["status"] = "pending"
    else:
        for w in words:
            w["status"] = "pending"

    return jsonify({
        "name": wl["name"],
        "description": wl.get("description", ""),
        "words": words,
        "filename": filename,
    })


# ═══════════════════════════════════════════════════════════════════════
# API — Article Rewriting
# ═══════════════════════════════════════════════════════════════════════

@app.route("/api/rewrite", methods=["POST"])
def api_rewrite():
    """Rewrite an article with injected target vocabulary.

    Body: {"article_id": N, "wordlist": "ms_core.json", "max_words": 8}
    Returns rewritten paragraphs + injected words list.
    """
    user = _require_user()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    body = request.get_json(silent=True) or {}
    article_id = body.get("article_id")
    wordlist_fn = body.get("wordlist", "ms_core.json")
    max_words = body.get("max_words", 8)

    if article_id is None:
        return jsonify({"error": "article_id required"}), 400

    # Check wordlist exists before doing anything expensive
    wl = load_wordlist(wordlist_fn)
    if not wl:
        return jsonify({"error": "Word list not found"}), 404

    article = get_article_by_id(int(article_id))
    if not article:
        return jsonify({"error": "Article not found"}), 404

    lock = _get_user_lock(user)
    with lock:
        try:
            from article_rewriter import rewrite_article_for_wordlist
            result = rewrite_article_for_wordlist(
                article, wordlist_fn, user, max_words=max_words
            )
        except Exception as e:
            return jsonify({"error": f"Rewrite failed: {e}"}), 500

    if not result:
        return jsonify({"error": "Rewrite failed — no words available or API error"}), 500

    return jsonify({
        "article_id": article_id,
        "paragraphs": result["rewritten_paragraphs"],
        "injected_words": result["injected_words"],
    })


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)

"""
Word list management for targeted vocabulary learning.

Word lists are stored as JSON files under data/wordlists/.
Each file is a dict with:
  - name: str
  - description: str
  - words: [{word, definition, pos?, example?}, ...]

User progress per word list is tracked in data/users/<user>/wordlist_progress.json:
  - { list_name: { "injected": [word, ...], "learned": [word, ...] } }
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_WORDLISTS_DIR = Path(__file__).parent / "data" / "wordlists"


def _ensure_dir() -> None:
    _WORDLISTS_DIR.mkdir(parents=True, exist_ok=True)


def list_wordlists() -> list:
    """Return all available word lists (name + description only)."""
    _ensure_dir()
    lists = []
    for f in sorted(_WORDLISTS_DIR.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            lists.append({
                "name": data.get("name", f.stem),
                "description": data.get("description", ""),
                "count": len(data.get("words", [])),
                "filename": f.name,
            })
        except Exception:
            continue
    return lists


def load_wordlist(filename: str) -> Optional[dict]:
    """Load a full word list by filename (e.g. 'ms_core.json')."""
    path = _WORDLISTS_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_wordlist_words(filename: str) -> list:
    """Return just the word entries from a word list."""
    wl = load_wordlist(filename)
    if not wl:
        return []
    return wl.get("words", [])


def create_wordlist(name: str, description: str, words: list) -> str:
    """Create a new word list. Returns the filename."""
    _ensure_dir()
    filename = name.lower().replace(" ", "_") + ".json"
    data = {
        "name": name,
        "description": description,
        "words": words,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = _WORDLISTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename


# ── Progress tracking ──

def _progress_path(username: str) -> Path:
    from pathlib import Path as _Path
    return _Path(__file__).parent / "data" / "users" / username / "wordlist_progress.json"


def load_progress(username: str) -> dict:
    """Load word list progress for a user. Returns {list_name: {injected:[], learned:[]}}."""
    p = _progress_path(username)
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(username: str, progress: dict) -> None:
    """Save word list progress for a user."""
    p = _progress_path(username)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def mark_words_injected(username: str, list_name: str, words: list) -> None:
    """Record that specific words were injected into an article."""
    progress = load_progress(username)
    entry = progress.setdefault(list_name, {"injected": [], "learned": []})
    for w in words:
        if w not in entry["injected"]:
            entry["injected"].append(w)
    save_progress(username, progress)


def mark_words_learned(username: str, list_name: str, words: list) -> None:
    """Record that specific words from a word list have been learned."""
    progress = load_progress(username)
    entry = progress.setdefault(list_name, {"injected": [], "learned": []})
    for w in words:
        if w not in entry["learned"]:
            entry["learned"].append(w)
    save_progress(username, progress)


def get_pending_words(filename: str, username: str) -> list:
    """Return words from a word list that haven't been injected or learned yet."""
    all_words = get_wordlist_words(filename)
    if not all_words:
        return []
    wl = load_wordlist(filename)
    list_name = wl["name"] if wl else filename
    progress = load_progress(username)
    entry = progress.get(list_name, {})
    done = set(entry.get("injected", []) + entry.get("learned", []))
    return [w for w in all_words if w["word"] not in done]


def pick_words_to_inject(filename: str, username: str, count: int = 8) -> list:
    """Pick N words from a word list that haven't been used yet.

    Prioritises words that are neither injected nor learned.
    Returns up to *count* word entries.
    """
    pending = get_pending_words(filename, username)
    if len(pending) <= count:
        return pending
    # Simple deterministic pick: first N pending
    return pending[:count]

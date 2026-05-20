"""
Article rewriter using DeepSeek LLM to naturally inject target vocabulary.

Takes an article + a list of target words → returns a rewritten article
where those words replace simpler equivalents in the text.

Caching: rewritten articles are cached in data/cache/rewrites/ to avoid
unnecessary API calls for the same article + word list combination.
"""

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Optional

# DeepSeek API configuration
DEEPSEEK_API_KEY = "REDACTED"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

_CACHE_DIR = Path(__file__).parent / "data" / "cache" / "rewrites"


def _cache_key(article_id: int, word_list_filename: str, count: int) -> str:
    raw = f"{article_id}:{word_list_filename}:{count}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_path(cache_key: str) -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _CACHE_DIR / f"{cache_key}.json"


def _load_from_cache(cache_key: str) -> Optional[dict]:
    path = _cache_path(cache_key)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Cache valid for 7 days
        age = time.time() - data.get("cached_at", 0)
        if age < 7 * 86400:
            return data
    return None


def _save_to_cache(cache_key: str, data: dict) -> None:
    data["cached_at"] = time.time()
    path = _cache_path(cache_key)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_rewrite_prompt(article: dict, target_words: list, max_words: int) -> str:
    """Build a prompt for the LLM to rewrite the article with injected words.

    The prompt instructs the model to naturally incorporate target vocabulary
    while keeping the article appropriate for middle-school readers.
    """
    paragraphs = article.get("paragraphs", [])
    original = "\n\n".join(p["text"] for p in paragraphs)

    word_list = "\n".join(
        f"- {w.get('word','')}: {w.get('definition','')}"
        for w in target_words[:max_words]
    )

    return f"""You are an English teacher creating reading materials for Chinese middle-school students (ages 12-15).

TASK: Rewrite the following English news article. Replace {max_words} simpler words or phrases with the target vocabulary words listed below. The rewrite should sound completely natural — a native English speaker should not notice any forced vocabulary.

ORIGINAL ARTICLE:
{original}

TARGET VOCABULARY (use {max_words} of these):
{word_list}

RULES:
1. Replace simpler words with target words where they fit naturally. Example: change "found" to "discovered", "place" to "environment".
2. Do NOT just insert words awkwardly. If a word truly doesn't fit, skip it.
3. Keep the same number of paragraphs and the same overall meaning.
4. Keep the language at a middle-school reading level (grades 6-8).
5. The rewritten article should be roughly the same length as the original.
6. Maintain the original paragraph structure — one paragraph per line, separated by blank lines.
7. Output ONLY the rewritten article text, with paragraphs separated by blank lines. No explanations, no markdown formatting, no additional text.

REWRITTEN ARTICLE:"""


def rewrite_article(
    article: dict,
    target_words: list,
    max_words: int = 8,
    *,
    api_key: str = DEEPSEEK_API_KEY,
) -> Optional[dict]:
    """Rewrite an article to inject target vocabulary words.

    Args:
        article: Article dict with 'id', 'paragraphs' (list of {text, translation})
        target_words: List of word dicts [{word, definition, pos}, ...]
        max_words: Max number of target words to inject
        api_key: DeepSeek API key

    Returns:
        Dict with {rewritten_paragraphs: [...], injected_words: [...]} or None on failure.
    """
    article_id = article.get("id", 0)

    # Build cache key (use first 10 target words for key stability)
    words_sig = ",".join(sorted(w["word"] for w in target_words[:20]))
    cache_key = _cache_key(article_id, words_sig, max_words)

    cached = _load_from_cache(cache_key)
    if cached:
        return cached.get("result")

    # Limit target words
    selected = target_words[:max_words]

    prompt = build_rewrite_prompt(article, selected, max_words)

    try:
        import urllib.request

        body = json.dumps({
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "You are a skilled English teacher who rewrites articles for students. You output only the rewritten text with no extra commentary."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        content = result["choices"][0]["message"]["content"].strip()

        # Parse rewritten paragraphs (split by blank lines)
        rewritten_paragraphs = _parse_rewritten(content, article)

        # Detect which words were actually used
        full_text = " ".join(rewritten_paragraphs)
        injected_words = []
        for w in selected:
            if re.search(r'\b' + re.escape(w["word"]) + r'\b', full_text, re.IGNORECASE):
                injected_words.append(w["word"])

        output = {
            "rewritten_paragraphs": rewritten_paragraphs,
            "injected_words": injected_words,
        }

        # Cache the result
        _save_to_cache(cache_key, {"result": output})

        return output

    except Exception as e:
        print(f"[rewriter] DeepSeek API error: {e}")
        return None


def _parse_rewritten(content: str, article: dict) -> list:
    """Parse LLM output into list of paragraph text strings.

    Attempts to match the paragraph count of the original article.
    """
    # Split by double newlines
    parts = re.split(r'\n\s*\n', content.strip())
    # Filter out non-paragraph lines (headers, notes, etc.)
    paragraphs = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip lines that look like meta-commentary
        if part.startswith("REWRITTEN") or part.startswith("Note:") or part.startswith("Here"):
            continue
        # Must have at least one sentence
        if len(part.split()) >= 5:
            paragraphs.append(part)

    # Match original paragraph count if possible
    orig_count = len(article.get("paragraphs", []))
    if len(paragraphs) > orig_count:
        # Merge extras into last paragraphs
        while len(paragraphs) > orig_count:
            paragraphs[-2] = paragraphs[-2] + " " + paragraphs[-1]
            paragraphs.pop()

    return paragraphs


def rewrite_article_for_wordlist(
    article: dict,
    wordlist_filename: str,
    username: str,
    max_words: int = 8,
) -> Optional[dict]:
    """High-level helper: pick words from a word list and rewrite the article.

    Returns None if no words available or rewrite fails.
    """
    from wordlist import load_wordlist, pick_words_to_inject, mark_words_injected

    wl = load_wordlist(wordlist_filename)
    if not wl:
        return None

    target_words = pick_words_to_inject(wordlist_filename, username, max_words)
    if not target_words:
        return None

    result = rewrite_article(article, target_words, min(max_words, len(target_words)))
    if result:
        mark_words_injected(username, wl["name"], result.get("injected_words", []))

    return result

# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Vocab in News — a personalized English vocabulary learning app for Chinese middle-school students. Users read news articles where target vocabulary words are naturally integrated via LLM rewriting. See docs/design.md for full design.

## Development Commands

```bash
# Start local server
cd src && python server.py
# Runs on http://127.0.0.1:5001

# Run tests
python -m pytest tests/ -v
```

## Deployment

Remote server: DigitalOcean droplet at `188.166.172.192` (root). SSH key is configured.

```bash
./deploy.sh
```

This pushes to GitHub, then SSHes to the server to `git pull` and restart via `restart.sh`. The live app is at **http://188.166.172.192:5001/**.

## Architecture

- **Backend**: Flask (server.py), port 5001, session-based auth (Flask session cookie)
- **Storage**: Per-user JSON files under `src/data/users/<name>/`
- **Frontend**: Server-rendered Jinja2 templates + vanilla JS (index.html, home.html, quiz.html, wordlist.html, words.html)
- **Vocab engine**: vocab_service.py — ~210 word difficulty DB, tokenize(), _lookup(), stem_word()
- **Word lists**: wordlist.py — curated vocab lists (TOEFL, CET4, MS Core, etc.), progress tracking
- **LLM rewriter**: article_rewriter.py — DeepSeek API integration for article rewriting, 7-day JSON cache
- **Dictionary fallback**: Free Dictionary API (https://api.dictionaryapi.net/) for words not in vocab DB
- **CSS**: Single file `src/static/style.css` — cartoon theme, blue/amber palette, responsive

## Key Files

| File | Purpose |
|------|---------|
| src/server.py | Main Flask app, all API endpoints |
| src/vocab_service.py | Word difficulty DB, tokenizer, stemming |
| src/wordlist.py | Word list CRUD, progress tracking, word injection |
| src/article_rewriter.py | DeepSeek LLM article rewriting with cache |
| src/templates/*.html | Jinja2 templates for each page |
| src/static/style.css | All styles (cartoon blue theme) |
| deploy.sh | One-command deploy to production |
| restart.sh | Remote server restart script (called by deploy.sh) |

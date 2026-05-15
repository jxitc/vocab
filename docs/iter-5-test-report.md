# Iter 5 - Test Report

**Date:** 2026-05-16  
**Tester:** QA (初中英语水平学习者 persona)  
**App URL:** http://127.0.0.1:5001

---

## Summary

| Section | Test | Result |
|---------|------|--------|
| A | Level Selector | PASS |
| B | Article Switcher | PASS |
| C | Cross-Level Word Filtering | PASS |
| D | Regression | PASS |

**Overall: 4/4 PASS**

---

## A. Level Selector

### A.1 Level buttons visible

All four level buttons (小学 | 初中 | 高中 | 大学) are visible in the header, displayed inline after "难度:" label.

**PASS**

### A.2 Default level

Upon first visit (clean localStorage), the default active level is 初中.

**PASS**

### A.3 Word count per level (Planet article)

| Level | Unique Highlighted Words | Words |
|-------|--------------------------|-------|
| 小学 | 3 | discovery, planet, discover |
| 初中 | 6 | discovery, planet, confirmed, surface, extremely, discover |
| 高中 | 8 | discovery, telescope, planet, solar, confirmed, surface, extremely, discover |
| 大学 | 10 | discovery, telescope, planet, solar, confirmed, surface, extremely, atmosphere, evidence, discover |

Word count increases as expected with level difficulty. Each level filters appropriately:
- 小学: most basic words only
- 大学: includes advanced words like "atmosphere", "evidence", "telescope"

**PASS**

### A.4 Level badge text

Active level is visually indicated on the button itself (button marked `[active]` in DOM). Switching levels changes which button is active and updates the word highlighting immediately.

**PASS**

---

## B. Article Switcher

### B.1 Article cards visible

Two article cards are displayed between the header and the instruction panel:
1. "A Teenager Discovered a New Planet While Doing a School Project" (科技日报, 2026-05-15)
2. "Giant Pandas Are No Longer Endangered, but Their Survival Still Needs Help" (中国日报, 2026-05-10)

The active article card has `class="article-card active"`.

**PASS**

### B.2 Default article

After clearing localStorage, the default article is the planet discovery one.

**PASS**

### B.3 Switch to pandas article

Clicking the pandas card:
- Page title changes to "Giant Pandas Are No Longer Endangered..."
- Article content changes (paragraphs, source, date)
- Highlighted words change to match the pandas article
- Level (初中) persists across article switch
- 6 highlighted words at 初中 level: planet, global, communities, developed, methods, research

**PASS**

### B.4 Switch back to planet article

Clicking the planet card restores the planet article content, title, and highlighted words. Level persists.

**PASS**

---

## C. Cross-Level Word Filtering (Pandas article)

### C.1 Words per level

| Level | Count | Words |
|-------|-------|-------|
| 小学 | 3 | planet, global, communities |
| 初中 | 6 | planet, global, communities, developed, methods, research |
| 大学 | 10 | planet, vulnerable, global, species, communities, developed, methods, research, considered, extremely |

### C.2 Paragraph-level distribution at 大学

- Paragraph 1: 5 words (planet, vulnerable, global, species, communities)
- Paragraph 2: 0 words (simpler narrative about bamboo/habitat)
- Paragraph 3: 5 words (developed, methods, research, considered, extremely)
- Paragraph 4: 0 words (conclusion, simpler language)

No single paragraph is overloaded with highlighted words. Paragraph 2 and 4 naturally contain simpler vocabulary, which is correct behavior.

### C.3 Quality of filtering

- 小学: only truly basic words (planet, global, communities) -- appropriate for elementary level
- 大学: adds advanced vocabulary (vulnerable, species, considered, extremely) -- appropriate for university level
- Words are progressively revealed, not randomly assigned

**PASS**

---

## D. Regression Tests

### D.1 Word clicking + popup

Clicking "planet" in the article text opens a popup overlay containing:
- Close button (x)
- The word: "planet"
- Part of speech: "n."
- Chinese definition: "行星"
- "朗读" (read aloud) button

After clicking, the word in the text turns green (`background-color: rgb(212, 237, 218)`) with class `word difficult clicked-before`.

**PASS**

### D.2 Translation toggle

Clicking "▶ 显示翻译" on paragraph 1:
- Toggle changes to "▼ 隐藏翻译"
- Full Chinese translation appears below the paragraph
- Translation quality is good (natural Chinese, preserves meaning)
- Clicking again hides the translation

**PASS**

### D.3 Word panel updates

Word panel shows all highlighted words with Chinese definitions and speaker icons. After clicking "planet" in the text, the word state updates from yellow (unlearned) to green (learned). The word panel reflects the current level and article.

**PASS**

### D.4 Finish button

Clicking "我读完了！" button:
- Button changes to "已完成 ✓" (disabled)
- Shows encouraging message: "太棒了！你今天读了一篇英语新闻，又进步了一点！"
- Shows stats: "学习了 X 个生词", "共点击 X 次"
- Message tone is warm and encouraging, matching the persona's expectations

**PASS**

### D.5 Speaker icons

Each highlighted word in both the article text and the word panel has a "点击听发音" element with an associated speaker icon. These are visible and interactive.

**PASS**

### D.6 localStorage: level persistence

1. Switched level from 初中 to 大学
2. Refreshed the page
3. Level persisted as 大学 (userLevel: 4 in localStorage)
4. Highlighted word count matched 大学 level (10 words)

**PASS**

### D.7 localStorage: article persistence

1. Switched article from planet (articleId: 0) to pandas (articleId: 1)
2. Refreshed the page
3. Article persisted as pandas
4. Level also persisted (大学)

**PASS**

---

## Notes

1. **favicon.ico 404**: The app returns 404 for `/favicon.ico`. Non-blocking cosmetic issue.
2. **Default article when localStorage has stale data**: If a previous session set articleId to 1 in localStorage, the pandas article loads first instead of the planet article (default). This is correct behavior -- it respects user preference.
3. **Word count progression is smooth**: The filtering algorithm correctly scales difficulty from 3 words (小学) to 10 words (大学) on the planet article, and 3 to 10 on the pandas article.
4. **Paragraph-level filtering is reasonable**: No single paragraph gets overloaded. Simpler paragraphs (like the bamboo habitat description) naturally have fewer or no highlighted words.

---

## Screenshots

| Screenshot | Description |
|------------|-------------|
| `screenshot-level-chuzhong.png` | Planet article at 初中 (6 words) |
| `screenshot-level-xiaoxue.png` | Planet article at 小学 (3 words) |
| `screenshot-level-gaozhong.png` | Planet article at 高中 (8 words) |
| `screenshot-level-daxue.png` | Planet article at 大学 (10 words) |
| `screenshot-pandas-article.png` | Pandas article at 初中 (6 words) |
| `initial-state.png` | Clean initial state (before localStorage clear) |

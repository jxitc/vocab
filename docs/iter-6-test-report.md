# Iter 6 Test Report

**Date:** 2026-05-16
**Tester Persona:** 初中英语水平学习者 (Junior high English level)
**App URL:** http://127.0.0.1:5001

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| A. "我认识这个词" Button | PASS | Full flow works including persistence and "重新学习" |
| B. "我的词库" Panel | PASS | Toggle, counts, lists, and remove all work |
| C. Third Article (Esports) | PASS | Content, translations, and word selection all good |
| D. Favicon | PASS | No 404 or any console errors |
| E. Regression | PASS | All core features still working |

**Overall: 5/5 PASS**

---

## A. "我认识这个词" Button

### Test Steps & Results

1. **Click yellow highlighted word -> popup appears**
   - Clicked "planet" (yellow highlighted) in the panda article.
   - Popup appeared showing: word "planet", POS "n.", definition "行星", "朗读" button, and **"我认识这个词" button**.
   - PASS

2. **Click "我认识这个词" -> word loses yellow highlighting**
   - Clicked "我认识这个词".
   - "planet" immediately lost its yellow highlight in the article body (no longer `data-difficult="true"`, no cursor-pointer).
   - "本课生词" count dropped from (10个) to (9个).
   - PASS

3. **Popup button text changed to "重新学习"**
   - After clicking "我认识这个词", the popup button text changed to **"重新学习"**.
   - PASS

4. **Refresh page -> persistence in localStorage**
   - Refreshed the page (navigated to same URL).
   - "planet" remained un-highlighted (plain text in article).
   - "我的词库" badge still showed the updated count.
   - PASS

5. **"重新学习" -> word becomes yellow again**
   - Marked "global" as known, then clicked "重新学习" in its popup.
   - "global" immediately became yellow again (`data-difficult="true"`).
   - PASS

### Notes
- All state persisted correctly across page refreshes (localStorage).
- The "重新学习" flow correctly restored words to the highlighted state.

---

## B. "我的词库" Panel

### Test Steps & Results

1. **Find and click "我的词库" toggle**
   - Button located in the header area with badge showing current count.
   - Initially showed "我的词库 (1)" then updated to "(2)" after first mark.
   - PASS

2. **Panel expands with correct sections**
   - Panel expanded showing two sections:
     - **"我认识的词"** (Words I Know) with count
     - **"我的生词本"** (My Vocabulary Notebook) with count
   - PASS

3. **Mark 2 words as known -> counts update**
   - Marked "vulnerable" and "global" as known (in addition to "planet").
   - Panel updated: "我认识的词 (3)", "我的生词本 (3)".
   - Header badge updated to "我的词库 (6)" (total words tracked).
   - PASS

4. **"我的生词本" shows learned words**
   - "我的生词本" listed: planet, vulnerable (with definition "脆弱的；易受伤害的"), global (with definition "全球的").
   - PASS

5. **Click "x" -> word removed from list**
   - Clicked "x" on "vulnerable" in the "我认识的词" section.
   - "vulnerable" was removed from the panel list.
   - PASS

6. **Removed word becomes highlighted again in article**
   - After removal from known words, "vulnerable" was yellow highlighted again in the article (`data-difficult="true"`).
   - PASS

### Notes
- Each word in "我认识的词" shows its difficulty level (小学/大学) and Chinese definition.
- The "x" button reliably removes words from tracking.

---

## C. Third Article (Esports)

### Test Steps & Results

1. **Switch to third article**
   - Clicked the esports card in the article switcher.
   - Title updated to: "How Esports Became a Billion-Dollar Industry That Rivals Traditional Sports".
   - PASS

2. **Title and content load correctly**
   - Source: 环球时报, Date: 2026-05-12.
   - Content: 4 paragraphs covering esports history, growth factors, professional player lifestyle, and China's role.
   - Topic is engaging for the target persona (gaming/sports/tech enthusiast).
   - PASS

3. **Chinese translations present for each paragraph**
   - Each paragraph has a "显示翻译" (Show Translation) toggle button.
   - Clicking reveals full Chinese translation. Example: "就在十年前，大多数人还认为电子游戏只是青少年的有趣爱好..."
   - PASS

4. **Highlighted words appropriate for level**
   - 10 words highlighted: global, professional, traditional, factors, major, strategy, opponents, reaction, employ, maintain.
   - Words span from elementary (小学) to college (大学) level - appropriate mix.
   - Chinese definitions provided for all: 全球的, 专业的, 传统, 因素, 主要的, 策略, 对手, 反应, 雇用, 维持.
   - PASS

### Notes
- Word "professional" appears 5 times in the article, all correctly highlighted.
- Article length and word count (10 new words) is at the upper bound of the persona's tolerance (8-12).

---

## D. Favicon

### Test Steps & Results

1. **Check browser console for 404 errors**
   - Zero console errors throughout the entire test session.
   - PASS

2. **Check network requests for favicon failures**
   - No failing favicon.ico requests detected.
   - PASS

### Notes
- Clean console across all page navigations and interactions.

---

## E. Regression Tests

### Test Steps & Results

1. **Level selector**
   - Switched from default level to "初中" (junior high).
   - Word list changed from (10个) to (6个) as expected.
   - Words were filtered appropriately for the selected level.
   - PASS

2. **Article switcher**
   - Switched between all 3 articles: Teenager Discovered a Planet, Giant Pandas, Esports.
   - All loaded correctly with proper titles, content, and word lists.
   - PASS

3. **Word clicking + popup**
   - Clicked highlighted words ("planet", "vulnerable", "global", "discovery").
   - Popup consistently appeared with: word, part of speech, Chinese definition, speaker button, and "我认识这个词" button.
   - PASS

4. **Translation toggle**
   - Clicked "显示翻译" on paragraphs in the esports article.
   - Chinese translations appeared inline below each paragraph.
   - PASS

5. **Word panel updates**
   - "本课生词" count updated as words were marked known/un-known.
   - Word list dynamically adjusted (removed known words, re-added on "重新学习").
   - PASS

6. **Finish button**
   - Clicked "我读完了！" button.
   - Message displayed: "太棒了！你今天读了一篇英语新闻，又进步了一点！学习了 4 个生词，共点击 4 次"
   - Message is encouraging and uses Chinese (matches persona requirement).
   - PASS

7. **Speaker icons**
   - Speaker icons (🔊 with "点击听发音" tooltip) present on all highlighted words in the article.
   - Clicking a speaker icon triggered audio playback.
   - PASS

### Notes
- All regression tests passed. No regressions detected from previous iterations.
- The encouraging finish message in Chinese aligns well with the persona's expectation of being encouraged rather than evaluated.

---

## Persona Perspective Observations

| Persona Expectation | Assessment |
|---------------------|------------|
| 80%+ words recognized | ~10 highlighted words per 200-400 word article = reasonable ratio |
| One-click Chinese translation | Available per paragraph via "显示翻译" button |
| Chinese definitions for words | Every highlighted word has Chinese definition in popup and word list |
| Content matches interests | Esports article directly targets the gaming/sports interest |
| Encouragement over criticism | "太棒了！你又进步了一点！" is encouraging |
| "I already know this" option | "我认识这个词" button provides this exit |

### Minor Observations
- The esports article has 10 highlighted words which is at the upper bound of the persona's tolerance (8-12 max). Consider reducing to 8 for the default level.
- "professional" appears 5 times in the esports article (highlighted each time) - this repetition may feel redundant. Consider only highlighting first occurrence.
- After marking a word as known and refreshing, a replacement word appeared to maintain the 10-word target ("experts" replaced "planet"). This auto-refill behavior may confuse users who expect the word list to shrink.

---

## Test Environment
- **Browser:** Playwright (Chromium)
- **OS:** macOS (Darwin)
- **App:** Local Flask dev server on port 5001
- **Articles tested:** All 3 available (Teenager/Planet, Pandas, Esports)
- **Levels tested:** Default and 初中

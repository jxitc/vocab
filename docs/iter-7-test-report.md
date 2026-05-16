# Iter 7 Test Report

**Date:** 2026-05-16
**Tester Persona:** 初中英语水平学习者 (Junior high English level)
**App URL:** http://127.0.0.1:5001

---

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| A. Word Deduplication | PASS | Repeated words only highlighted on first occurrence |
| B. Reading Stats | PASS | Stats bar shows and persists across refreshes with correct counts |
| C. New Articles (Diver & Crows) | PASS | Both articles load with correct content and vocabulary |
| D. Regressions | PASS | All core features working, zero console errors |

**Overall: 4/4 PASS**

---

## A. Word Deduplication

### Test Steps & Results

1. **Navigate to esports article (id=2, level=4 大学)**
   - Switched difficulty level to 大学 (4).
   - Clicked esports card in the article switcher.
   - Article loaded with 10 highlighted difficult words.
   - PASS

2. **Check "professional" deduplication**
   - The word "professional" appears 5 times in the article text.
   - Only the **first occurrence** (paragraph 1: "professional gamers") is highlighted yellow (`data-difficult="true"`).
   - The other 4 occurrences (paragraphs 3 and 4: "professional esports player", "professional teams", "professional player", "professional sport") are NOT highlighted (`data-difficult="false"`, class `normal`).
   - PASS

3. **Check "traditional" deduplication**
   - The word "traditional" appears 2 times.
   - Only the **first occurrence** (paragraph 1: "many traditional sporting events") is highlighted.
   - The second occurrence (paragraph 4: "traditional athletics") is NOT highlighted.
   - PASS

4. **Check "esports" (not in vocabulary list)**
   - The word "esports" appears 9 times in the article.
   - All 9 occurrences are NOT highlighted (correct -- proper noun not in vocabulary list).
   - PASS

5. **Check all 10 highlighted words are unique**
   - Highlighted words: global, professional, traditional, factors, major, strategy, opponents, reaction, employ, maintain.
   - All 10 are unique -- no duplicate highlighting across the article.
   - PASS

6. **Cross-check with crows article (id=4)**
   - "experiments" and "experiment" are both highlighted (different word forms -- singular vs plural).
   - This is correct behavior: deduplication operates on exact lowercase match, not stemming. Different word forms are treated as separate vocabulary items.
   - PASS (by design)

### Notes
- Deduplication is robust: the server-side logic computes all difficult words, sorts by first appearance, limits to maxHighlights, then the template only highlights the first occurrence of each word.
- The `seen_highlighted` set in `build_paragraphs_with_tokens()` correctly prevents repeat highlighting within a single article.

---

## B. Reading Stats

### Test Steps & Results

1. **Initial state (fresh localStorage)**
   - Loaded the app with cleared localStorage.
   - Reading stats bar was NOT visible (no articles read yet).
   - PASS

2. **Click yellow words then click "我读完了!"**
   - Navigated to esports article, clicked 3 yellow words (global, traditional, factors).
   - Clicked "我读完了!" button.
   - Reading stats bar appeared showing:
     - 已读: **1** 篇
     - 已学: **3** 词
     - 连续: **1** 天
   - PASS

3. **Verify counts are correct**
   - 已读 1: correct (one article completed).
   - 已学 3: correct (3 unique words clicked).
   - 连续 1: correct (today's date recorded in lastReadDates).
   - PASS

4. **Refresh page -- stats persist**
   - Refreshed the page (`window.location` reload).
   - Reading stats bar still visible with identical values:
     - 已读: 1, 已学: 3, 连续: 1
   - PASS

5. **Complete a second article -- stats accumulate**
   - Switched to Pandas article (id=1), clicked "我读完了!".
   - Stats updated to:
     - 已读: **2** 篇
     - 已学: **4** 词 (accumulated from both sessions)
     - 连续: 1 天
   - PASS

6. **Streak calculation verified**
   - The streak calculation correctly identifies today's read date and counts consecutive days.
   - Only one unique date recorded, so streak = 1.
   - PASS

### Notes
- Stats are stored in localStorage key `vocab_in_news_stats`.
- totalWordsLearned syncs from learnedWords count on each mark-as-learned event (only increments, never decreases).
- Edge case handled: streak doesn't count if neither today nor yesterday is in the date list.

---

## C. New Articles

### Article 3: Diver/Olympic Gold (id=3)

1. **Switch to article**
   - Clicked the 4th article card: "A 14-Year-Old Diver Won Gold and Made History at the Olympic Games".
   - Article loaded immediately with correct metadata.
   - PASS

2. **Title, source, date**
   - Title: "A 14-Year-Old Diver Won Gold and Made History at the Olympic Games"
   - Source: 体育周刊
   - Date: 2026-05-08
   - PASS

3. **Chinese translations**
   - 4 paragraphs, each with a "显示翻译" toggle.
   - Paragraph 1 translation: "上周，一名14岁的中国跳水选手在夏季奥运会上夺得金牌..."
   - All translations are complete and accurate.
   - PASS

4. **Highlighted vocabulary**
   - 5 words highlighted at level 初中: extraordinary (非凡的；特别的), mental (精神的；心理的), detail (细节), challenge (挑战), achieve (实现；达到).
   - All have Chinese definitions in the word panel and popup.
   - PASS

### Article 4: Crows Intelligence (id=4)

1. **Switch to article**
   - Clicked the 5th article card: "Scientists Discover That Crows Can Solve Problems as Well as a Seven-Year-Old Child".
   - Article loaded immediately with correct metadata.
   - PASS

2. **Title, source, date**
   - Title: "Scientists Discover That Crows Can Solve Problems as Well as a Seven-Year-Old Child"
   - Source: 自然探索
   - Date: 2026-05-14
   - PASS

3. **Chinese translations**
   - 4 paragraphs, each with a "显示翻译" toggle.
   - All translations present and accurate.
   - PASS

4. **Highlighted vocabulary**
   - 10 words highlighted at level 大学: published (出版；发表), journal (期刊；日志), similar (相似的), research (研究), experiments (实验), experiment (实验), evidence (证据), logical (合乎逻辑的), species (物种), abilities (能力).
   - "experiments" and "experiment" appear as separate entries (singular vs plural).
   - All have Chinese definitions.
   - PASS

### Notes
- Both new articles maintain the same paragraph structure (4 paragraphs each) with translations.
- Article content is engaging and appropriate for the target persona (sports achievement story + animal intelligence discovery).
- Word difficulty distribution is appropriate.

---

## D. Regression Tests

### 1. Level Selector
- Switched between all 4 levels (小学, 初中, 高中, 大学) on the crows article.
- Word count changed appropriately: 大学=10 words, 初中=6 words (correct per maxHighlights config).
- Active button state persisted across article switches.
- PASS

### 2. Article Switcher
- Shows all 5 articles with correct titles, sources, and dates.
- Active article highlighted with green border.
- Clicking any card loads the corresponding article.
- PASS

### 3. Word Clicking + Popup
- Clicked "published" (yellow highlighted word) in crows article.
- Popup appeared with: word "published", POS "v.", definition "出版；发表", speaker button, and "我认识这个词" button.
- Popup positioned correctly near the clicked word.
- Closing popup with "x" button works.
- Clicking outside popup closes it.
- PASS

### 4. "我的词库" Panel
- Panel toggle button shows badge count (e.g., "我的词库 (5)").
- Panel expands to show two sections:
  - "我认识的词" with count and list.
  - "我的生词本" with count and list.
- Each word shows definition and difficulty level badge.
- "x" button removes words from tracking.
- Removing from "我认识的词" re-highlights the word in the article.
- Removing from "我的生词本" clears the learned state.
- PASS

### 5. "我认识这个词" / "重新学习" Flow
- Clicking "我认识这个词" on a highlighted word:
  - Word immediately loses yellow highlight (class changes to `normal known-word`, `data-difficult="false"`).
  - "本课生词" count decrements.
  - Popup button text changes to "重新学习".
  - Word is added to "我认识的词" section.
- Clicking "重新学习":
  - Article reloads, word regains yellow highlight.
  - "本课生词" count increments back.
  - Popup button text reverts to "我认识这个词".
  - Word removed from "我认识的词" section.
- PASS

### 6. Translation Toggle
- "显示翻译" toggles to reveal Chinese translation below each paragraph.
- Arrow rotates from ▶ to ▼ when open.
- Label changes from "显示翻译" to "隐藏翻译".
- Clicking again hides the translation.
- PASS

### 7. Finish Button
- Clicking "我读完了!" shows encouraging message in Chinese: "太棒了！你今天读了一篇英语新闻，又进步了一点！"
- Displays learned word count and total click count.
- Button changes to "已完成 ✓" and becomes disabled.
- Reading stats are recorded on finish.
- PASS

### 8. Console Errors
- Zero console errors across the entire test session.
- No failed network requests.
- PASS

---

## Persona Perspective Observations

| Persona Expectation | Assessment |
|---------------------|------------|
| 80%+ words recognized | ~5-10 highlighted words per article = reasonable ratio |
| One-click Chinese translation | Available per paragraph via "显示翻译" button |
| Chinese definitions for words | Every highlighted word has Chinese definition in popup and word list |
| Content diversity | 5 articles across different topics (science, nature, sports, technology) |
| Encouragement over criticism | "太棒了！你今天读了一篇英语新闻，又进步了一点！" is encouraging |
| Progress tracking | Reading stats bar shows cumulative learning progress |
| Word repetition management | Deduplication prevents highlighting the same word multiple times |
| "I already know this" option | "我认识这个词" button with "重新学习" reversal |

### Minor Observations

1. **"experiments" and "experiment" as separate entries**: In the crows article, both "experiments" (plural) and "experiment" (singular) are highlighted as separate vocabulary items. While this is correct at the exact-match deduplication level, a future improvement could use stemming to group inflectional variants (consider for Iter 8).

2. **Replacement word behavior after "重新学习"**: When a user marks a word as known and then clicks "重新学习", the article reloads. Because maxHighlights is fixed, the word may be re-added but a different word might get displaced. This behavior is by design but could surprise users. Consider adding a brief notification explaining the change.

3. **"professional" deduplication visibility**: In paragraph 3 of the esports article, the non-highlighted "professional" appears multiple times. Users might wonder why only the first one was yellow. The help hint explains this but some users may miss it. Consider adding a subtle visual indicator (e.g., underline) for non-first occurrences of vocabulary words.

4. **Reading stats streak granularity**: The streak only counts whether an article was completed on a given day, not the number of articles. This is appropriate for the MVP but a future iteration could add more granular daily goal tracking.

5. **5 articles total**: With 5 articles in the rotation (up from 3 in Iter 6), the content variety is good for the MVP phase. The switch from the maximum of 2 articles at level 小学 to 10 at level 大学 provides good progression.

---

## Test Environment
- **Browser:** Playwright (Chromium)
- **OS:** macOS (Darwin 25.2.0)
- **App:** Local Flask dev server on port 5001
- **Articles tested:** All 5 (Teenager/Planet, Pandas, Esports, Diver/Olympic, Crows)
- **Levels tested:** All 4 (小学, 初中, 高中, 大学)
- **localStorage:** Tested with fresh (cleared) and persisted state

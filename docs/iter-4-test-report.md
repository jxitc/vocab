# Iter 4 Test Report -- Vocab in News

**Date**: 2026-05-16  
**Tester persona**: Chinese middle-school student (vocab ~1000-1500, needs Chinese fallback)  
**App**: Flask at http://127.0.0.1:5001  
**Iter 4 scope**: Loading UX, panel interactivity, bidirectional sync, solar definition  

---

## Summary

All 4 new features work correctly. No regressions found.

---

## A. Loading UX -- PASS

- The loading element (`正在为你准备今天的新闻...` with spinner) exists in the HTML inside `#loadingState`.
- On page load, `fetch('/api/article')` fires; the spinner + message is visible until the response arrives.
- Since the article is served from a local JSON file, the loading state flashes very briefly (under 50ms on localhost). A middle-school student on a slow connection would see it for longer.
- After fetch completes, `loadingEl.style.display = 'none'` hides the loader and the article renders.
- **Verdict**: Implementation is correct. The loading message is too brief to screenshot on localhost but the code path is sound.

## B. Panel Interactivity -- PASS

Tested by clicking 3 words in the "本课生词" panel: "discovery", "telescope", "planet".

| Action | Result |
|---|---|
| Click "discovery" in panel | Popup appears with `discovery` / `n.` / `发现` |
| | Panel item gets `learned` class (turns green background) |
| | Both article instances get `clicked-before` class (turn green) |
| Click "telescope" in panel | Popup with `telescope` / `n.` / `望远镜` |
| | Panel item green, both article instances green |
| Click "planet" in panel | Popup with `planet` / `n.` / `行星` |
| | Panel item green, all 4 article instances green |
| Popup close button (x) | Closes popup correctly |
| Popup "朗读" button | Present and clickable, triggers speechSynthesis |

Screenshot taken after 3 panel clicks showing the green visual state.

## C. Bidirectional Sync -- PASS

Clicked "solar" directly in the article body (not the panel):

- **Article word**: `clicked-before` class applied (turns green) -- PASS
- **Panel item**: `learned` class applied (turns green) -- PASS
- **Popup**: Shows `solar` / `adj.` / `太阳的；太阳系的` -- PASS
- **Both directions work**: clicking in panel syncs to article, clicking in article syncs to panel.

## D. Solar Definition -- PASS

- In the word panel, "solar" shows the definition `太阳的；太阳系的` (visible before any click).
- In the popup (after clicking), it shows `adj.` / `太阳的；太阳系的`.
- This matches the Iter 4 requirement to replace the previous English-only definition with a proper Chinese definition.

## E. Regression Checks -- PASS

| Feature | Status | Notes |
|---|---|---|
| Speaker icons in panel | PASS | 6 speaker icons, one per word |
| Speaker icons in article | PASS | 11 speaker icons, one per difficult-word occurrence |
| Popup "朗读" button | PASS | Present when speechSynthesis is supported |
| Translation toggle | PASS | Arrow rotates (▶ -> ▼), label changes (显示翻译 -> 隐藏翻译), Chinese text appears correctly |
| Finish button | PASS | "我读完了！" button present |
| Finish button nudge (0 words) | PASS | Dialog: "你还没有点击任何生词哦！..." with Cancel/OK options |
| Nudge cancel | PASS | Returns to reading, button unchanged |
| Nudge confirm | PASS | Completes session, shows "学习了 0 个生词" with encouragement |
| Completion message | PASS | "太棒了！你今天读了一篇英语新闻，又进步了一点！" with learned count and click count |
| Finished button disabled | PASS | After completion, button shows "已完成 ✓" and is disabled |
| localStorage persistence | PASS | Progress saved across reloads; clearing localStorage resets state |

## Issues Found

None. All Iter 4 features work as specified and no regressions were detected.

## Notes for Next Iteration

- The loading message is functional but nearly invisible on localhost. Consider adding an artificial 500ms minimum display time or a `setTimeout` delay so developers and testers can visually confirm the loading state.
- The nudge dialog text is well-written for the target persona (encouraging, explains what yellow words mean, gives an easy out).
- The `数据来源:` label in the header could be considered -- currently reads `来源: 科技日报`, which is fine for the demo but should eventually reflect real sources.

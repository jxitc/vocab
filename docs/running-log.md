# Running Log

## 2026-05-15 — Iteration 0 启动

### 当前状态
- 项目初始化，仅含设计文档
- Dev Agent 正在构建 Iter 0 基线产品

### 环境
- macOS Darwin 25.2.0
- Python 3.9.6 + pip 21.2.4
- git repo 已初始化

### Iter 0
- [x] 基础 Flask 服务器 + China Daily 文章
- [x] Test: 5个致命缺陷 — 静态英文墙，生词率18-20%
- 教训: 没中文翻译/查词/互动 = 用户马上离开

### Iter 1 (5c48a8b)
- [x] vocab_service.py: ~200词难度DB + 中文释义 + 词干提取
- [x] 交互式前端: 点击生词弹出中文释义
- [x] 段落级中文翻译 (显示/隐藏)
- [x] 新文章: 青少年发现行星 (适龄话题)
- [x] "我读完了！"按钮 + 鼓励语
- [x] Test: 发现P0数字bug、13个生词过多、弹窗问题

### Iter 2 (39e95fe)
- [x] P0: 正则修复，数字和连字符词正常显示
- [x] 高亮词限制为6个 (从13个降到6个)
- [x] 非生词改为有道词典 (替代Merriam-Webster)
- [x] 弹窗关闭按钮z-index修复
- [x] "学了0个词"提醒逻辑
- [x] 提示文字解释黄→绿颜色系统
- [x] 29 tests passing

## Iter 3 (e296573)
### 已实现
- [x] Web Speech API TTS发音 (speaker图标 + popup朗读按钮, rate 0.85)
- [x] 生词汇总面板 "本课生词 (6个)" — 实时更新黄→绿色状态
- [x] localStorage进度持久化 (已学单词 + 完成状态)
- [x] 客户端渲染 fetch(/api/article) — Phase A平台迁移
- [x] 优雅降级 (SpeechSynthesis不可用时隐藏图标)
- [x] 29 tests passing
### 测试结果 (35c901b)
- All P0 bugs fixed ✓
- Audio UI ✓ (实际发音质量需手动验证)
- localStorage ✓
- 4 issues: 面板不可交互/状态不同步/无loading/solar释义不准确

## Iter 4 (cbfe78a)
### 已实现
- [x] 生词面板可点击交互 (弹窗 + 标记已学)
- [x] 面板与文章学习状态双向同步
- [x] 加载动画 "正在为你准备今天的新闻..."
- [x] solar释义: "太阳的" → "太阳的；太阳系的"
- [x] 29 tests passing
### 测试结果 (abffaba)
- All 4 features pass, zero regressions

## Iter 5 (6739979)
### 已实现 — 测试通过 (9961add)
- [x] 4级难度选择器 + 逐级高亮 (3/6/8/10词)
- [x] 第二篇文章 (熊猫保护)
- [x] 文章切换UI + localStorage持久化
- [x] 52 tests passing

## Iter 6 (93e2936)
### 已实现
- [x] "我认识这个词" 按钮 — 标记已知词，词条不再高亮，可"重新学习"恢复
- [x] "我的词库" 面板 — "我认识的词" + "我的生词本"，可移除
- [x] 已知词过滤 — 前后端协同：localStorage + API ?known= 参数
- [x] 第三篇文章 — 电竞产业 (环球时报)
- [x] SVG favicon 防止404
- [x] 67 tests passing
### 测试结果 (Iter 6 test)
- All 5 features PASS, zero regressions
- Minor: "professional" 出现5次全部高亮 (冗余)，自动补充生词可能让用户困惑


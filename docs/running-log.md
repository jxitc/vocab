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

## Iter 7
### 已实现
- [x] 生词去重 — 同一词只高亮首次出现 (server.py 首现跟踪)
- [x] 阅读统计 — 已读篇数/已学词数/连续天数 (localStorage + 显示)
- [x] 2篇新文章 — 跳水奥运冠军 (体育周刊) + 乌鸦智力研究 (自然探索)
- [x] 67 tests passing
### 测试结果 (Iter 7 test)
- All 4 features PASS, zero regressions
- Minor: experiments/experiment 未合并词形；"重新学习"后的自动补充可能困惑用户

## Iter 8
### 已实现
- [x] 读后小测验 — 读完文章后自动显示选择题 (英文词→选中文释义)
- [x] 每个生词一题，4选1，即时批改 + 总分鼓励语
- [x] 切换文章时测验自动重置
- [x] 67 tests passing

## Iter 9
### 已实现
- [x] 生词复习卡片 — "我的词库"中的"复习"按钮启动翻转卡片模式
- [x] 点击卡片翻转查看释义，选择"记得"/"忘了"
- [x] 复习结果 + 鼓励语，可"再复习一次"
- [x] 67 tests passing

## Iter 10
### 已实现
- [x] 阅读计时器 — 从文章加载到"我读完了"的耗时统计
- [x] 阅读速度 — 词/分钟 (WPM) 显示
- [x] 花费时间和速度显示在完成消息中
- [x] 67 tests passing

## Iter 11
### 已实现
- [x] 每日阅读目标 — 可设置1/2/3/5篇目标，阅读统计栏显示进度 (如 1/2 篇)
- [x] 目标达成庆祝 — 完成每日目标后弹出 🎉 动画提示
- [x] localStorage 持久化目标设置和今日进度，跨天自动重置
- [x] 78 tests passing

## Iter 12
### 已实现
- [x] 词干去重 — 使用 stem_word() 替代精确匹配合并词形变体 (confirmed/confirm, protecting/protect)
- [x] stem_word() 公有化 + 10个新测试
- [x] 已知局限: 单轮词干提取 -s规则优先，experiments/experiment 暂不合并
- [x] 78 tests passing

## Iter 13
### 已实现
- [x] 文章阅读状态 — 已读/未读/当前阅读 标记
- [x] 文章卡片显示"新"橙色徽章 (未读) / "已读"灰色徽章 / "阅读中"绿色徽章
- [x] localStorage 持久化已读文章ID集合
- [x] 78 tests passing

## Iter 14
### 已实现
- [x] 键盘快捷键 — 1-4切换难度, ← → 切换文章, Esc关闭弹窗/面板
- [x] 帮助提示更新含快捷键说明
- [x] 输入框/下拉框内不触发快捷键
- [x] 78 tests passing

## Iter 15
### 已实现
- [x] 2篇新文章 — 12岁女孩发明海洋清洁装置 (环保时报) + 盲人钢琴家在卡内基音乐厅演出 (文化周刊)
- [x] 文章总数从5篇增至7篇，话题覆盖环保/科技/体育/自然/文化/励志
- [x] 78 tests passing

## Iter 16
### 已实现
- [x] 成就徽章系统 — 11个里程碑徽章 (初次阅读/阅读达人/阅读大师/词海初探/词汇达人/词海霸主/三日坚持/七日之约/满分测验/速读高手/全能学者)
- [x] 徽章解锁动画Toast + 成就面板展示 (已解锁/未锁定带日期)
- [x] 成就数据localStorage持久化 (ACHIEVEMENT_KEY)
- [x] 2篇新文章 — 16岁少年为农村儿童建免费编程学校 (科技日报) + 中国宇航员从空间站直播物理课 (新华社)
- [x] 文章总数从7篇增至9篇
- [x] 修复: recordArticleRead 多余闭合括号 (pre-existing brace bug)
- [x] 78 tests passing

## Iter 17
### 已实现
- [x] 段落朗读 — 每段文字旁🔊图标，点击用TTS朗读整段内容
- [x] 朗读时段落高亮 (绿色左边框 + 浅绿背景)
- [x] 字号控制 — 小/中/大三档 (16px/19px/23px)，偏好持久化至localStorage
- [x] 78 tests passing

## Iter 18
### 已实现
- [x] 深色模式 — 🌙/☀️ 切换按钮，全局dark主题覆盖
- [x] 系统偏好检测 — 首次访问自动跟随系统prefers-color-scheme
- [x] 偏好持久化至localStorage
- [x] 修复: applyFontSize函数头在编辑中丢失
- [x] 78 tests passing

## Iter 19
### 已实现
- [x] 2篇新文章 — 15岁女孩发明低成本太阳能净水器 (环球科学) + 双语学习可延缓大脑衰老5年 (健康日报)
- [x] 文章总数从9篇增至11篇
- [x] 词库搜索 — "我的词库"面板增加搜索输入框，实时过滤已学/已知词汇
- [x] 78 tests passing

## Iter 20
### 已实现
- [x] 词汇导出 — "📥 导出词汇"按钮，下载.txt文件含词汇+释义+统计
- [x] 2篇新文章 — 18岁艺术家50米海洋壁画 (艺术日报) + 中学生设计无车城市获奖 (城市日报)
- [x] 文章总数从11篇增至13篇，话题覆盖科技/自然/体育/环保/文化/太空/教育/健康/艺术/城市规划
- [x] 78 tests passing

## Iter 21
### 已实现
- [x] 随机文章按钮 — "🎲 换一篇看看"，随机切换到非当前文章
- [x] 生词学习进度环 — 词面板标题旁SVG环形进度条，实时显示已学/总百分比
- [x] updateProgressRing() 联动 markWordAsLearned/renderWordPanel/restoreFinishedState
- [x] 78 tests passing

## Iter 22
### 已实现
- [x] 阅读理解题 — 读后小测验后展示2道T/F判断题，测试文章内容理解
- [x] 即时批改 + 总分鼓励语 (🌟/👍/🔍)
- [x] server.py API响应含comprehension字段
- [x] 2篇新文章 — 15岁女孩创建语言学习应用 (教育周刊) + 中学生社区花园改造 (城市日报)
- [x] 文章总数从13篇增至15篇，话题覆盖科技/自然/体育/环保/文化/太空/教育/健康/艺术/城市规划/语言学习/社区
- [x] 78 tests passing

## Iter 23
### 已实现
- [x] 文章卡片字数统计 — 每张文章卡片显示词数和预估阅读时间 (如"251词 · 2分钟")
- [x] server.py /api/articles 返回 wordCount 字段
- [x] 阅读记录面板 — 📖 可折叠面板显示已读文章列表及阅读时间，点击可跳转
- [x] readArticleDates 追踪 + localStorage 持久化，兼容旧数据
- [x] 78 tests passing

## Iter 24
### 已实现
- [x] 话题标签 — 每篇文章分配话题标签 (太空/自然/体育/环保/文化/教育/健康/艺术/城市/科技)
- [x] 文章卡片显示彩色话题标签，暗色模式适配，10种话题各有配色
- [x] server.py API返回topic字段
- [x] 2篇新文章 — 13岁国际象棋冠军 (体育周刊) + 高中生植树机器人 (科技日报)
- [x] 文章总数从15篇增至17篇
- [x] 78 tests passing

## Iter 25
### 已实现
- [x] 单词上下文句子 — 点击生词弹窗显示该词在原文中的完整句子，高亮目标词
- [x] extractSentence() 基于标点边界自动提取句子，支持中英引号
- [x] 上下文区 italic 灰色样式，暗色模式适配，弹窗关闭时自动隐藏
- [x] 78 tests passing

## Iter 26
### 已实现
- [x] 文章收藏 — ☆/★ 收藏按钮 (文章标题旁)，切换收藏状态，localStorage持久化
- [x] 收藏文章卡片标识 — 已收藏文章卡片标题旁显示 ★
- [x] 阅读位置记忆 — 切换文章前保存滚动位置，返回时自动恢复
- [x] 收藏按钮暗色模式适配 — .fav-btn .starred 完整暗色样式
- [x] 78 tests passing

## Iter 27
### 已实现
- [x] 话题筛选 — 文章列表上方话题标签筛选栏，点击话题只显示相关文章，「全部」恢复
- [x] 2篇新文章 — 14岁作曲家创作交响乐全球首演 (文化周刊) + 跳舞是最强脑力运动 (健康日报)
- [x] 文章总数从17篇增至19篇，10个话题各有1-3篇
- [x] 话题筛选栏暗色模式适配
- [x] 78 tests passing


# Platform Migration Analysis

## Current Architecture (Iter 1)

```
┌─────────────────────────────────────────┐
│  Flask Server (Python)                  │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │ Jinja2      │  │  Business Logic  │  │
│  │ Templates   │  │  (vocab_service) │  │
│  │ (server-side│  │  (pure Python)   │  │
│  │  rendered)  │  │                  │  │
│  └─────────────┘  └──────────────────┘  │
└─────────────────────────────────────────┘
```

**问题**: 前端和后端通过 Jinja2 模板紧耦合。HTML 在服务端渲染，数据直接注入模板。如果要移植到小程序或 App，整个前端都得扔掉重写。

## 迁移路径

### Phase A: Web → API + SPA（建议在 Iter 3-5 完成）

```
┌──────────────────┐     REST API      ┌──────────────────┐
│  Static Frontend │ ◄───────────────► │  Flask API       │
│  (HTML/JS/CSS)   │    JSON only      │  (Python)        │
│                  │                   │                   │
│  客户端渲染       │                   │  /api/article    │
│  fetch() API     │                   │  /api/vocab      │
│                  │                   │  (pure JSON)     │
└──────────────────┘                   └──────────────────┘
```

**工作量**: 小（1-2 轮迭代）。把 Jinja2 渲染改成 JS fetch + DOM 渲染。后端基本不变，只去掉 `render_template`。

**收益**: 前后端分离后，三端（Web / 小程序 / App）共享同一套 API。

### Phase B: Web → 微信小程序

```
┌──────────────────┐     REST API      ┌──────────────────┐
│  微信小程序       │ ◄───────────────► │  Flask API       │
│  (WXML/WXSS/JS)  │    JSON only      │  (不变)          │
│                  │                   │                   │
│  重写 UI 层      │                   │  零改动          │
│  wx.request()    │                   │                  │
└──────────────────┘                   └──────────────────┘
```

**工作量**: 中等。需要重写整个 UI 层（WXML ≠ HTML，WXSS ≠ CSS），但 API 和业务逻辑完全复用。

**关键差异**:
| 特性 | Web | 微信小程序 |
|------|-----|-----------|
| 标记语言 | HTML | WXML (类似但不同) |
| 样式 | CSS | WXSS (CSS 子集) |
| HTTP | fetch/XMLHttpRequest | wx.request |
| 弹窗 | div + CSS | 原生组件 |
| 发音 | Web Audio API | wx.createInnerAudioContext |
| 外部链接 | window.open | 不支持，需用 web-view |
| 包大小 | 无限制 | 单包 ≤ 2MB，总包 ≤ 20MB |
| 登录 | 自建 | wx.login + 微信 unionID |

**迁移时间估算**: 2-4 周（1 人全职），前提是 API 已经分离。

### Phase C: Web/小程序 → 独立 App

```
┌──────────────────┐     REST API      ┌──────────────────┐
│  React Native /  │ ◄───────────────► │  Flask API       │
│  Flutter App     │    JSON only      │  (不变)          │
│                  │                   │                   │
│  重写全部 UI     │                   │  零改动          │
│  原生能力        │                   │                  │
└──────────────────┘                   └──────────────────┘
```

**工作量**: 最大。全部 UI 重写，但 API 复用。

**RN vs Flutter**:
- **React Native**: 如果团队熟悉 JS/React，学习成本低。社区成熟，但原生模块调试麻烦。
- **Flutter**: 性能更好，UI 一致性高。Dart 语言需要学习。适合重视动画和 UI 的产品。

**迁移时间估算**: 4-8 周（1 人全职）MVP 版本。

## 迁移难度总结

| 阶段 | API 改动 | UI 改动 | 整体难度 | 时间(1人) |
|------|---------|---------|---------|-----------|
| Web Jinja2 → Web SPA | 小（去模板） | 中（JS 重写） | ⭐⭐ | 1-3 天 |
| Web SPA → 微信小程序 | 零 | 大（全重写） | ⭐⭐⭐ | 2-4 周 |
| Web SPA → RN/Flutter App | 零 | 大（全重写） | ⭐⭐⭐⭐ | 4-8 周 |

**核心结论**: 只要尽早完成 Phase A（前后端分离），后面的迁移成本可控。API 和业务逻辑（vocab_service 等）是完全可复用的。

## 从 Iter 2 开始要注意的事

### 立即做（低成本高收益）
1. **新功能优先走 API** — 新数据接口用 JSON API，不在模板里拼数据
2. **业务逻辑独立模块** — vocab_service.py 已经是好例子，继续保持
3. **前端用 fetch() 而不是服务端渲染** — 渐进式把 Jinja2 渲染改成 JS 客户端渲染
4. **避免依赖浏览器特有 API** — 如果要用 `window.open`，封装一层；如果要用 Web Audio，也封装

### 跨平台 TTS 注意事项 (2026-05-16 补充)
当前 Web 版使用浏览器 `SpeechSynthesis` API，但各平台情况不同：

| 平台 | TTS 方案 | 状态 |
|------|---------|------|
| **macOS Chrome/Safari** | SpeechSynthesis (Samantha/Daniel 等系统语音) | 可用 |
| **Windows Chrome** | SpeechSynthesis (Microsoft David/Zira) | 可用 |
| **Linux Chrome** | SpeechSynthesis (通常无语音，需装 espeak) | ❌ 不可用 |
| **iOS Safari** | SpeechSynthesis (系统语音，质量好) | 可用 |
| **Android Chrome** | SpeechSynthesis (Google TTS) | 可用 |
| **微信小程序** | `wx.createInnerAudioContext` + 服务端 TTS | 需重写 |
| **React Native** | `react-native-tts` 或服务端 TTS | 需重写 |
| **Flutter** | `flutter_tts` 或服务端 TTS | 需重写 |

**当前降级策略**：代码已做 `speechSupported` 检测，不支持的平台自动隐藏喇叭图标，不影响核心阅读体验。

**未来方案**：考虑服务端 TTS（如 Google Cloud TTS / AWS Polly）生成音频文件，通过 `/api/audio/{word}` 返回。优点是全平台统一、可缓存；缺点是有延迟和成本。建议 Iter 10+ 再处理。

### 暂时不用做（过度设计）
- 不需要现在就引入 React/Vue 框架（vanilla JS 够用）
- 不需要现在就拆分微服务
- 不需要引入跨平台框架

### 适合的迭代节奏
```
Iter 2-N:   逐步把前端改成 fetch API + 客户端渲染（Phase A）
Iter N+1:   开始微信小程序 UI 开发（Phase B）
Iter N+2:   评估独立 App 需求
```

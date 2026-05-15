# Iteration Methodology

## 双 Agent 迭代开发流程

```
┌──────────────────────────────────────────────────────────────┐
│                        Iteration Loop                         │
│                                                              │
│   ┌──────────────┐          ┌──────────────┐                 │
│   │  Dev Agent   │ ──build→ │   Product    │                 │
│   │              │          │  (web app)   │                 │
│   └──────────────┘          └──────┬───────┘                 │
│                                    │                         │
│                                    ▼                         │
│                           ┌──────────────┐                  │
│                           │  Test Agent  │                  │
│                           │ (playwright) │                  │
│                           │              │                  │
│                           │ persona:     │                  │
│                           │ user_role.md │                  │
│                           └──────┬───────┘                  │
│                                  │                          │
│                                  ▼                          │
│                           ┌──────────────┐                  │
│                           │  Gap Report  │                  │
│                           │ (issues.md)  │                  │
│                           └──────┬───────┘                  │
│                                  │                          │
│                                  ▼                          │
│   ┌──────────────┐     ┌───────────────┐                    │
│   │  Dev Agent   │ ◄── │  Next Iter    │                    │
│   │  (next iter) │     │  Task Spec    │                    │
│   └──────────────┘     └───────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

## 核心原则

1. **Dev Agent 和 Test Agent 隔离** — 用独立 sub-agent，防止 context 污染
2. **Test Agent 必须以 user_role.md 为 persona** — 不能走形式，必须感同身受
3. **每轮只解决上一轮发现的最关键 gap** — 不一口气做太多
4. **git commit 记录每个 milestone** — 每轮迭代至少一个 commit
5. **单元测试覆盖核心逻辑** — 算法模块必须有测试
6. **running log 持续更新** — 记录遇到的问题、决策和教训

## 迭代节奏

- **Iter 0**: 最小可用产品 — 能看一篇新闻
- **Iter 1**: 解决 Iter 0 发现的核心 gap
- **Iter 2-N**: 逐步逼近 design.md 中的最终设计
- **收敛判断**: 连续 3 轮 Test Agent 无新增关键 gap

## 每次迭代的交付物

- [ ] 代码变更（含单元测试）
- [ ] git commit
- [ ] Test Agent 的 gap report
- [ ] 更新 running log

## 文档索引

- [design.md](design.md) — 产品设计文档
- [user_role.md](user_role.md) — 目标用户画像（Test Agent persona）
- [iteration-methodology.md](iteration-methodology.md) — 本文件
- [running-log.md](running-log.md) — 运行日志

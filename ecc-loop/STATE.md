# JiuwenSwarm → ECC Loop 改进 STATE

**日期**: 2026-06-21
**状态**: ✅ 全部完成

---

## 目标

基于 JiuwenSwarm 深度研究，实施三个关键改进：
1. **A. build_context_seed 序列化** — STATE.md → 结构化 seed.json
2. **B. 热更新机制** — skill 重扫描 cron job
3. **C. FastOneShotPlanner 分层规划** — 简单/复杂 query 分流复盘

---

## 当前状态

```
ECC Loop 状态：
- skill: ~/.hermes/skills/ecc-to-hermes-loop/
- observations: ~/.hermes/observations.jsonl (567条)
- evolution_pipeline cron job: 每2小时 ✅
- build_seed: 不存在（待创建）
- skill 热重载: 不存在（待创建）
- 分层复盘: 不存在（待创建）
```

---

## 执行阶段

### Phase A: build_context_seed 序列化
- [x] Task A1: 分析 STATE.md 序列化结构 → 简单 markdown，无版本号/时间戳
- [x] Task A2: 创建结构化 seed.json → ~/.hermes/ecc-loop-seed.json ✅
- [x] Task A3: seed 模块 ecc_seed.py → load/save/update/mark_complete ✅

### Phase B: 热更新机制
- [x] Task B1: 分析 skill 热加载机制 → hermes skills audit 可重扫描
- [x] Task B2: 创建 skill 重扫描脚本 → rescan_skills.sh ✅
- [x] Task B3: seed 版本追踪 → 69 个 instinct skills 已写入 ✅

### Phase C: 分层复盘
- [x] Task C1: 分析现有复盘逻辑 → P6 Evaluator RAG + ecc_reflect.py 快慢路径
- [x] Task C2: 实现分层复盘策略 → fast_path (≤20 chars) + full_path (complex) ✅

---

## 当前阶段

**Phase A - Task A1**: 分析 STATE.md 序列化结构

---

## 回滚点

- Phase A: 删除 seed.json，保留原 STATE.md
- Phase B: 删除 cron job，回滚 skill 版本追踪
- Phase C: 删除分层复盘脚本

---

## 验证标准

- seed.json 序列化/反序列化正常
- skill 重扫描 cron job 每小时运行
- 分层复盘测试通过

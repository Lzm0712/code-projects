# JiuwenSwarm 完整研究计划

> **For Hermes:** 使用 tdd-guide-agent 逐任务执行，每个任务验证通过后再进入下一个。

**Goal:** 对 JiuwenSwarm 项目完成系统性源码研究，提炼可借鉴的架构设计、Agent 协作模式、工具调用机制，输出结构化研究报告。

**Architecture:** JiuwenSwarm 是基于 openJiuwen 的智能 AI Agent，通过群组协作（Swarm）模式扩展 LLM 能力。项目包含核心 Agent 框架（jiuwenswarm/）、硬件盒子集成（jiuwenbox/）、部署脚本（deploy/docker）和测试套件（tests/）。

**Tech Stack:** Python 3.11-3.13, openJiuwen, 华为云 MaaS, 小艺开放平台

---

## 研究框架

### 阶段一：项目概览（1-2任务）

### Task 1: README + 项目结构

**Objective:** 理解项目定位、技术栈、生态位

**Files:**
- Read: `README.md`
- Read: `README_CN.md`
- Read: `pyproject.toml`

**Step 1: Read README**
- 阅读 README.md 和 README_CN.md，理解项目目标和核心特性
- 记录：项目解决的痛点、目标用户、核心功能列表

**Step 2: Read pyproject.toml**
- 记录：依赖包、Python 版本要求、入口点

**Step 3: Read TESTING.md**
- 理解测试策略和测试环境要求

**验收：** 能够用一句话描述 JiuwenSwarm 是什么，以及它的核心创新点。

---

### 阶段二：核心架构（3-5任务）

### Task 2: 核心包 jiuwenswarm/ 目录结构

**Objective:** 理解核心代码组织

**Files:**
- Read: `jiuwenswarm/` 目录结构

**Step 1: 列出所有 Python 文件**
```bash
find jiuwenswarm -name "*.py" | sort
```

**Step 2: 按文件名分类**
- Agent 类相关
- 工具/Tool 相关
- 通信/Communication 相关
- 协作/Coordination 相关

**验收：** 输出一张模块依赖图（可用文字描述）+ 核心类清单。

---

### Task 3: Agent 核心实现

**Objective:** 理解单个 Agent 的生命周期、状态管理、工具调用机制

**Files:**
- Read: `jiuwenswarm/agent.py` 或 `jiuwenswarm/core/`
- Read: `jiuwenswarm/tools.py` 或 `jiuwenswarm/tools/`

**Step 1: 找到 Agent 基类**
- 搜索 `class.*Agent` 定义
- 理解 Agent 的状态机设计

**Step 2: 找到工具调用机制**
- 搜索 `tool_call` 或 `function_call`
- 理解工具注册、选择、执行流程

**Step 3: 理解 Agent 间通信机制**
- 搜索 `send` / `receive` / `message`
- 理解 Swarm 中的信息传递模式

**验收：** 能够画出单个 Agent 的工作流程图（启动 → 感知 → 决策 → 执行 → 通信）。

---

### Task 4: Swarm 协作机制

**Objective:** 理解多个 Agent 如何协作、任务如何分解与汇总

**Files:**
- Read: `jiuwenswarm/swarm.py` 或 `jiuwenswarm/coordination/` 或 `jiuwenswarm/multi_agent.py`

**Step 1: 找到 Swarm/Coordinator 类**
- 搜索 `class.*Swarm` 或 `class.*Coordinator`

**Step 2: 理解任务分解策略**
- 任务如何分配给多个 Agent
- 结果如何汇总

**Step 3: 理解 Agent 注册与发现机制**
- Agent 如何加入 Swarm
- 如何感知其他 Agent 的能力

**验收：** 能够描述一个典型 Swarm 协作流程（任务进入 → 分解 → 分派 → 汇总 → 输出）。

---

### Task 5: 平台集成（华为云 MaaS + 小艺）

**Objective:** 理解与外部平台的集成方式

**Files:**
- Read: `jiuwenswarm/platforms/` 或相关集成代码
- Read: `packages/` 目录

**Step 1: 华为云 MaaS 集成**
- 搜索 `huawei` / `maas` / `model` 相关代码
- 理解模型调用封装

**Step 2: 小艺开放平台集成**
- 搜索 `xiaoyi` / `xiaoyu` 相关代码

**Step 3: openJiuwen 关系**
- 理解 jiuwenswarm 与 openJiuwen 的依赖关系

**验收：** 能够描述平台的适配器模式设计。

---

### 阶段三：工程化（2-3任务）

### Task 6: 测试体系

**Objective:** 理解测试策略和覆盖率

**Files:**
- Read: `tests/` 目录结构
- Read: `pytest.ini`
- Read: `run_tests.sh`

**Step 1: 测试文件分类**
- 单元测试 / 集成测试 / E2E 测试
- 测试 fixtures 和 mocks 策略

**Step 2: 运行测试**
```bash
cd /tmp && git clone --depth=1 https://github.com/openJiuwen-ai/jiuwenswarm.git
cd jiuwenswarm && bash run_tests.sh
```

**验收：** 测试通过率 + 测试覆盖率报告。

---

### Task 7: 部署架构

**Objective:** 理解生产环境部署方式

**Files:**
- Read: `deploy/` 目录
- Read: `docker/` 目录

**Step 1: 部署方式清单**
- Docker / K8s / 直接部署
- 环境变量配置

**Step 2: jiuwenbox 硬件盒子**
- 理解硬件集成方式

**验收：** 能够描述一套生产部署的最低要求。

---

### 阶段四：综合分析（1任务）

### Task 8: 可借鉴点 + ECC Loop 对标

**Objective:** 从研究中提炼对 ECC Loop 有价值的设计模式

**研究问题：**
1. **工具调用机制**：jiuwenswarm 的工具注册和调用模式 vs ECC Loop 的 tool_obs + instinct learning
2. **Agent 协作**：Swarm 模式是否可以借鉴到 ECC 的多角色协作
3. **固化机制**：jiuwenswarm 是否有类似"经验固化"的机制
4. **状态管理**：Agent 状态机设计 vs ECC 的 STATE.md 模式
5. **平台适配**：多平台集成架构 vs ECC 的 tool-observer 模式

**输出格式：**
```
## JiuwenSwarm 可借鉴设计

| 维度 | JiuwenSwarm 方案 | ECC Loop 当前方案 | 可借鉴程度 | 行动项 |
|------|------------------|-------------------|------------|--------|
| ...  | ...              | ...               | 高/中/低   | ...    |
```

**验收：** 输出完整研究报告 + 可操作的对标改进建议。

---

## 执行顺序

1. Task 1（项目概览）
2. Task 2（目录结构）
3. Task 3（Agent 核心）
4. Task 4（Swarm 协作）
5. Task 5（平台集成）
6. Task 6（测试体系）
7. Task 7（部署架构）
8. Task 8（综合分析）

每 Task 完成后记录笔记到 `~/.hermes/openclaw-patrol/research/2026-06-21-jiuwenswarm-notes.md`

---

## 依赖

- 需要能访问 GitHub（clone 源码）
- 测试运行需要 Python 3.11+

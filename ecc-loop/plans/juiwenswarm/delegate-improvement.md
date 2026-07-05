# JiuwenSwarm 蜂群机制 → ECC 借鉴方案

**来源**: `jiuwenswarm/agents/swarm/providers/member_rails.py`

---

## 当前 ECC delegate_task 的问题

```
delegate_task(goal="...", toolsets=["terminal","file"])
```

是**命令式**的——goal + toolsets 直接写死，没有声明层。

JiuwenSwarm 的问题是：**为什么需要一个中间声明层？**

---

## 蜂群机制核心：@harness_element + ConstructionInput

```python
# 1. 声明式注册（工厂函数）
@harness_element(
    kind=ElementKind.RAIL,
    name="swarm.skill_retrieval_prompt",
    description="Lightweight prompt guidance for skill retrieval"
)
def build_skill_retrieval_rail(
    input: SkillRetrievalPromptInput,  # ConstructionInput 子类
    params: dict,                      # spec 中的 params
    ctx: SwarmBuildContext               # 构建期上下文
) -> RuntimePromptRail | None:
    if not params.get("enabled"):
        return None
    # 从 input 提取 context 字段
    global_skills_dir = input.global_skills_dir
    return RuntimePromptRail(...)

# 2. ConstructionInput 定义构造参数来源
class SkillRetrievalPromptInput(ConstructionInput):
    global_skills_dir: str | None = context_field(
        attr="global_skills_dir",
        description="Global installed skills source directory.",
    )
    # 还有 param_field 从 params 提取
```

---

## 为什么比命令式好？

| 维度 | 命令式 (ECC 当前) | 声明式 (JiuwenSwarm) |
|------|------------------|---------------------|
| 构造时机 | 调用时立即执行 | 可延迟到 build time |
| 参数来源 | 全部在调用方 | 可从 config/context/params 多源 |
| 可序列化 | 无 | spec 可 JSON 化，跨进程传递 |
| 条件判断 | 调用方 if/else | provider 内返回 None 跳过 |
| 可测试性 | 依赖运行时 | 可在构造期验证 |

---

## ECC 可以借鉴的模式

### 1. DelegateSpec 声明式委托规格

```python
@dataclass
class DelegateSpec:
    """声明式委托规格（类比 RailSpec/SubAgentSpec）"""
    task_type: str                              # "research" / "coding" / "review"
    required_toolsets: list[str]                 # 类比 tools: list[BuiltinToolSpec]
    default_model: str | None = None
    max_rounds: int = 5
    condition: str | None = None                # "observations_count > 10" 等
    
    def to_manifest(self) -> dict:
        """序列化为 manifest，供 build() 使用"""
        return {
            "task_type": self.task_type,
            "required_toolsets": self.required_toolsets,
            ...
        }
```

### 2. DelegateContext（类比 SwarmBuildContext）

```python
@dataclass
class DelegateContext:
    """委托构造期的环境句柄"""
    session_id: str
    observations_path: Path
    skills_dir: Path
    current_phase: str
    metrics: dict
```

### 3. Provider 注册表（类比 _RAIL_PROVIDER_REGISTRY）

```python
_DELEGATE_PROVIDER_REGISTRY: dict[str, Callable] = {}

def register_delegate_provider(name: str, factory: Callable):
    _DELEGATE_PROVIDER_REGISTRY[name] = factory

# 使用
def resolve_delegate(spec: DelegateSpec, ctx: DelegateContext):
    factory = _DELEGATE_PROVIDER_REGISTRY.get(spec.task_type)
    if factory:
        return factory(spec.to_manifest(), ctx)
    return None
```

---

## 具体可实施的改进

### 方案 A: 轻量借鉴（不破坏现有接口）

在现有 `delegate_task` 基础上，增加 `spec` 参数：

```python
# 当前
delegate_task(goal="...", toolsets=["terminal"])

# 改进后（可选）
delegate_task(
    goal="...",
    toolsets=["terminal"],
    spec=DelegateSpec(task_type="coding", condition="observations_count > 10")
)
```

**好处**: 向后兼容，声明层是可选的

### 方案 B: 完全迁移（参考 JiuwenSwarm）

废弃 `goal + toolsets`，改用 `DelegateSpec`：

```python
delegate_task(
    spec=DelegateSpec(
        task_type="research",
        required_toolsets=["web", "file"],
        max_rounds=3
    ),
    context={"topic": "JiuwenSwarm 架构"}
)
```

**好处**: 完全可控，可序列化，可测试

---

## 推荐方案

**方案 A（轻量借鉴）**，理由：
1. 不破坏现有接口，用户可渐进迁移
2. JiuwenSwarm 的核心价值是声明层 + 构造期延迟，ECC 可先加声明层
3. 构造期逻辑（Provider）可以后续迭代

### 实施步骤

**Step 1**: 定义 `DelegateSpec` dataclass + `DelegateContext`
**Step 2**: `delegate_task` 工具增加 `spec` 可选参数
**Step 3**: 如果 `spec` 存在，走 Provider 解析；否则走老逻辑
**Step 4**: 添加 `test_delegate_spec.py` 测试

---

## JiuwenSwarm 蜂群机制关键源码

- `jiuwenswarm/agents/swarm/providers/member_rails.py` — 核心 `@harness_element` 用法
- `openjiuwen/agent_teams/harness/manifest.py` — `ConstructionInput`/`context_field`/`param_field` 定义
- `jiuwenswarm/agents/swarm/assembly.py` — enrich 流程

---

## 核心教训

JiuwenSwarm 蜂群的本质是：**把"构造什么"和"怎么构造"分离**。

- `RailSpec` / `SubAgentSpec` 是**声明**（"我要什么"）
- Provider 工厂是**构造**（"怎么造出来"）
- `ConstructionInput` 是**参数解析**（"从哪取参数"）

ECC 的 `delegate_task(goal, toolsets)` 是命令式——"怎么干"全在调用方，没有分离。

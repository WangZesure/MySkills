---
name: agent-work-frame
description: "Adaptive human-agent collaboration framework — feature-driven document orchestration. The core is simple: forward provides information, backward provides tests, middle iterates. Task features (knowledge_gap, needs_overview, needs_report, etc.) independently trigger enhancement modules that strengthen specific framework phases — no hard classification, no exclusive types. Full pipeline from requirements definition to paper-style report."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Agent-Orchestration, Task-Decomposition, Context-Management, Methodology]
    related_skills: [claude-code, writing-plans, subagent-driven-development, task-type-classification, workframe-to-report]
---

# Agent Work Frame — Adaptive Collaboration Framework

A structured methodology for human-agent collaboration. The framework is simple:

- **Forward（正向）** — 人提供信息，Hermes 填充 knowledge + reference
- **Backward（反向）** — Hermes 设计 testpoints，人批准
- **Middle（中间迭代）** — Hermes + Claude Code 交替执行

Task features (extracted by `task-type-classification`) independently trigger enhancement modules — deepening knowledge, adding overview decomposition, enabling report generation, etc. No hard classification. No exclusive types. Features stack.

## When to Use

- Any task where "just ask the agent to do it" leads to chaos — unclear scope, lost context, or inconsistent output
- Tasks where the difficulty profile is uncertain: you don't know if it's a 30-minute script or a 3-day project
- Research explorations, greenfield design, protocol implementation, or multi-artifact deliveries
- Tasks where quality requires traceability: the final report must show what was done, why, and how it was verified

## File Organization

```
[task]/
  rule.md              ← framework rules (one copy, global)
  backward/
    goal.md             ← task I/O specification (STABLE)
    testpoints.md       ← acceptance criteria (P0/P1/P2)
  forward/
    reference.md        ← research references (append-only)
    knowledge.md        ← atomic knowledge (append-only, living document)
    sections.md         ← sub-stage decomposition (optional)
  runtime/
    plan.md             ← execution plan with dependency graph (process: what we do when)
    memory.md           ← iteration log (append-only, versioned)
    overview.md         ← static decomposition of final deliverable (product: what it looks like)
    STATUS.md           ← session snapshot (≤20 lines, read first)
  workspace/            ← actual deliverables
  templates/            ← empty templates for new tasks
```

File classification:
| Class | Files | Rule |
|-------|-------|------|
| STABLE | goal.md, sections.md | Approved; changes require Change Log |
| ACCUMULATED | reference.md, knowledge.md | Append-only; can mark outdated |
| MUTABLE | runtime/* | Updated every iteration |

## Role Distribution (Human / Hermes / Claude Code)

In practice, the framework is used with a three-party split:

| Direction | Who | What |
|-----------|-----|------|
| **Forward (正向)** | Human → Hermes | Initial info: task docs, environment credentials, reference materials. Hermes populates forward/ (reference.md + knowledge.md) via reading + structured extraction. |
| **Backward (反向)** | Hermes | Testpoints (testpoints.md): design P0/P1/P2 checkpoints that verify goal.md outputs. Human approves. |
| **Middle iteration (中间迭代)** | Hermes + Claude Code | Simple tasks (code from tutorial, env setup, direct debugging) → Hermes does directly. Complex codebase understanding, deep refactoring, knowledge-gap tasks → delegate to Claude Code via `claude-code` skill. |
| **Final deliverable (最后交付)** | Hermes → Human | Paper-style report (see Deliverable Format below) showing design, results, visualization, testpoint pass/fail. |

**Key insight**: The human doesn't fill testpoints — Hermes proposes them from goal.md analysis. The human only approves. This keeps the human's role focused on domain judgment (is this the right test?) not mechanical enumeration.

### Stage 1: Research
- Read goal.md → search for existing solutions/papers/references
- Populate reference.md (source, relevance, key findings, extractable elements)
- Populate knowledge.md (atomic definitions, constraints, design impact)
- Deliverable: reference.md + knowledge.md

### Stage 2: Environment Setup
- Create workspace/ directory structure
- Install dependencies, configure toolchain
- Make everything agent-actionable (no human-in-the-loop for routine ops)
- For remote servers with password auth: see `references/ssh-askpass-pattern.md` (SSH_ASKPASS + base64 transfer, avoids Hermes interactive-SSH blocking)
- For DLP/MLU pycnnl platform quirks (ICS lab2, Cambricon): see `references/pycnnl-dlp-platform-quirks.md`
- For platform auto-grading submission pitfalls (ICS/Educg, zip structure, import paths, batch_size trap, HIDDEN exports): see `references/platform-autograding-pitfalls.md`
- For cross-version NumPy weight compatibility: use `scripts/convert_npy_protocol2.py` (Python 3.10+ NumPy → Python 3.7 NumPy 1.19). For root-cause explanation and pitfalls, see `references/numpy-pickle-cross-version.md`.
- For CPU convolution speed optimization (im2col): see `references/im2col-convolution-optimization.md`.
- Deliverable: workspace/ ready

### Stage 3: Sub-Stage Decomposition (optional)
- Trigger: task can't be designed in one mental pass, or has too many branches
- Fill sections.md with I/O contracts and states for each sub-stage
- Sub-stage detailed designs go to overview-[X].md
- Deliverable: sections.md

### Stage 4: Design & Test Planning
- Write overview.md using 3-layer description if needed
- Write testpoints.md: P0 (must-pass gate) / P1 (quality) / P2 (completeness)
- Initialize plan.md (plan-driven) or memory.md (iteration-driven)
- Deliverable: testpoints.md + plan.md or memory.md

### Stage 5: Iterate
Per-iteration cycle:
1. Read status: check runtime/ for current progress
2. Execute: complete next step
3. Verify: run testpoints (auto) or show to human (manual)
4. Update: plan.md status or memory.md entry
5. Grow: new understanding → knowledge.md
6. Refine: design changes → overview.md

Termination: all P0 testpoints pass + human confirmation.

**Blocking signal**: stuck on same element repeatedly → rewind to Stage 3 (decompose further) or Stage 1 (research more). Only monotonically increasing knowledge and testpoints guarantee convergence.

**Platform submission iteration**: When the execution environment differs from the design environment (e.g., auto-grading platform with unknown directory structure, missing libraries, different Python version), use a probe-then-fix micro-cycle:
1. Add debug output to entry points (print CWD, list directories, try multiple paths)
2. Submit once → read error + debug output
3. Fix the single blocking issue → resubmit
4. Repeat until clean pass

This is faster than trying to pre-guess all platform differences. One submission with debug output replaces multiple guesswork submissions.

### Stage 6: Deliver
- Integrate deliverables to workspace/
- Cross-check against goal.md
- Run all testpoints
- Append final version to memory.md
- Human sign-off against goal.md

## Feature Dispatch

任务先经过 `task-type-classification` 提取特征向量（F1~F10，每个 degree 0/1/2）。degree ≥ 1 的特征触发对应的增强模块。**特征叠加，不互斥。**

| 触发特征 | 增强模块 | 影响范围 |
|---------|---------|---------|
| `knowledge_gap` | **知识增强** | forward/: knowledge.md 升级为核心活文档；runtime/: plan 步骤拆 learn→design→verify 微循环 + P-K 检查 |
| `needs_overview` | **静态分解** | runtime/: 写 overview.md，按 cognitive distance 选层 |
| `needs_report` | **报告生成** | Stage 6 后自动触发 REPORT.md |
| `needs_research` | **外部调研** | forward/: 启 reference.md；knowledge.md 标注来源 |
| `has_ambiguity` | **澄清闸门** | Stage 2 前插入 clarify gate |
| `multi_stage` | **子阶段管理** | runtime/: sections.md + overview-[X].md |
| `needs_iteration` | **反馈循环** | runtime/: memory.md 版本递增；plan 不预设全部步骤 |
| `needs_parallel` | **并行标记** | runtime/ plan.md 标并行组；delegate_task 批量调度 |
| `high_stakes` | **验证增强** | backward/: testpoints.md 扩大 P0 覆盖 |
| `has_artifact` | **自查步骤** | runtime/ plan 每步尾追加自查子步骤 |

## Feature Extraction (First Step)

在进入框架之前，加载 `task-type-classification` skill 提取任务特征向量。产出：每个特征 degree(0/1/2) + 一句话证据。degree≥1 的特征触发上表对应的增强模块。

默认仅 `has_artifact=1`。其他特征按需触发——宁可漏判低估（后续人工纠正）也别过度触发导致冗余工程。

## ICS Platform Workflow

For ICS course experiments submitted to the Cambricon DLP platform (希冀), see `references/ics-platform-submission.md` for environment mismatches, pickle compatibility, pycnnl pitfalls, and submission formatting.

For ICS lab3 (VGG19 image classification) on the v6.1 LLM image, see `references/ics-lab3-v6.1-quirks.md` — covers changed paths, missing NumPy install, dead cv2 import, imageio pitfall, and 4-loop CPU timing.
For ICS lab3 style transfer (3.3), see `references/ics-lab3-style-transfer.md` — covers Conv/Pool backward, ContentLoss/StyleLoss implementation, and training loop.

## Deliverable Philosophy

The framework files (`forward/`, `backward/`, `runtime/`) are scaffolding for the agent, not the deliverable. The human's deliverable is a **self-contained paper-style report** (`workspace/REPORT.md`) they can read and understand without tracing framework files. Framework maintenance should be lightweight — update STATUS.md and plan.md as needed for context handoff, but don't over-maintain mid-process. The final report carries the weight.

## Quick-Start by Feature Vector

| Feature Vector | 入口 |
|----------------|------|
| 仅 `has_artifact=1`（简单任务） | Stage 5（跳过所有框架文件） |
| `knowledge_gap≥1` | Stage 1 → 5 → 6（全流程；learn→design→verify 微循环） |
| `needs_research≥1` | Stage 1 → 4 → 5（调研→设计→执行） |
| `has_ambiguity≥1` | Stage 2 前先 clarify → 再定入口 |
| `high_stakes=1` | Stage 4 前确保 testpoints.md P0 覆盖关键路径 |
| `needs_iteration=1` | Stage 5（memory.md 版本递增，不等 plan 完整） |
| `needs_report=1` | 任务结束后自动走 Stage 6 出 REPORT.md |

## Session Handoff Protocol

New session reads in this order:
```
1. STATUS.md           → sub-second context recovery
2. rule.md             → understand framework rules
3. goal.md             → understand task objective
4. plan.md (remaining steps) or memory.md (last 3 entries)
5. overview.md         → understand current design (if exists)
6. testpoints.md       → understand acceptance criteria
```

Context-constrained session: STATUS.md + goal.md + plan.md current step / memory.md last 3 > rule.md (cached, can skip) > others on demand.

## Design Overview (overview.md)

overview.md captures the **static decomposition of the final deliverable** — what the thing looks like, not how to build it. This is distinct from plan.md, which captures the **process** (Stage 1 → Stage 2 → ... → Stage 6).

| File | Scope | Question it answers |
|------|-------|-------------------|
| **plan.md** | Process (temporal) | What do we do first? Next? Dependencies? |
| **overview.md** | Product (static) | What does the final system look like? |

### How Many Layers to Write

Not every task needs all three layers. The decision is based on **cognitive distance** — how far apart the layers are in your mental model.

When choosing formalism, pick the most natural one: state machine, dataflow graph, call graph, pseudocode, type system, or plain architecture diagram. No need to force all three.

**Layer 1 — Interface Contract**: Invariants, type signatures, pre/post conditions. I/O table references goal.md.

**Layer 2 — Computational Model**: The formal model behind the interface — state machine, dataflow, call graph, pseudocode. Answers "what does it compute?"

**Layer 3 — Implementation Design**: Module decomposition, data flow, key algorithms. Traces to codebase structure. Readable by non-experts.

### Cognitive Distance Rule

| Cognitive Distance | Example | Write |
|-------------------|---------|-------|
| Layers overlap heavily — seeing the interface immediately implies the computation and implementation | Sorting algorithm, script that processes an image | **One layer** — pick whichever expresses it most naturally. No need to force the other two. |
| Moderate separation — interface is clear but computation or implementation has non-obvious choices | ML training pipeline, CLI tool with plugin system | **Two layers** — the ones with non-obvious gaps. |
| Wide separation — mathematical abstraction is hard to grasp, AND engineering constraints are complex, AND the gap between them is large | Research project with novel math + systems engineering | **All three layers** — each bridges a genuine cognitive gap. |

**Decision heuristic**: If you can write Layer 1 and immediately visualize Layers 2 and 3 without additional thinking, they're close enough to skip. Only write the layers that bridge non-obvious jumps.

For simple tasks where overview feels like overkill: a single architecture diagram (ASCII/PlantUML) with module I/O notes is sufficient. The framework is here for complexity, not ceremony.

## Framework Maintenance Policy

**Don't over-maintain runtime files during iteration.** The human cares about the final result, not the process artifacts. Keep `STATUS.md` and `plan.md` light — update only when a genuine checkpoint is reached or a dependency flips. Don't touch `knowledge.md` or `reference.md` after Stage 1 unless a genuine discovery occurs. Avoid writing `memory.md` entries for micro-iterations.

**The one deliverable that MUST be thorough is the final report** (REPORT.md). The human reads that to understand what happened. Make it self-contained: architecture, results, testpoint checklist, visualizations (even ASCII). No "see knowledge.md for details" — the report stands alone.

**Meta: avoid over-engineering.** When the framework starts generating its own complexity — new file categories, new classification dimensions, new templates — pause and ask: is this genuinely necessary, or am I making a decision with unexamined assumptions? The framework's value is in providing the minimum structure for complex tasks, not in becoming a complete taxonomy of all possible projects. When in doubt, err on the side of fewer files and simpler structure.

## Final Deliverable Format (Paper-Style Report)

After Stage 6 (all P0 testpoints pass), produce a **paper-style report** in `workspace/REPORT.md` for human sign-off. See the companion skill `workframe-to-report` for the exact file-to-chapter mapping and writing philosophy — the tl;dr is:

Framework files are notes (fragmented, agent-oriented); the report is a narrative (structured, human-oriented). Same information, different expression.

Template:

```
1. Abstract — one paragraph: what we did, how, key results
2. Problem Definition — input/output tables, constraints
3. Design — network architecture (ASCII art / PlantUML), module decomposition, data flow
4. Results — quantitative tables, performance comparison charts (ASCII bar charts), loss curves
5. Testpoint Verification — P0/P1/P2 table with pass/fail status per testpoint
6. Conclusion — summary + agent collaboration reflection
```

Include **visualizations** even if ASCII: bar charts for speed comparison, loss convergence curves, architecture diagrams (PlantUML). The report should be self-contained so the human can grasp the full project without reading the framework files.

- Judgments must have verifiable conditions; no fuzzy natural language
- Research conclusions cite sources (URL, file path, paper ID)
- Terms defined on first use; label [fact] vs [speculation]
- Prefer type signatures, state transitions; natural language only for motivation

## Sub-Stage Management

All sub-stage info centralized in sections.md:
- Name, I/O contract, status, design file path per sub-stage
- Detailed designs in overview-[X].md (each captures the static product of that sub-stage)
- Parent overview.md references children
- Default max 1 level depth; deeper requires justification

## Feature Modules（特征增强模块）

以下模块按需激活，互不冲突。每个模块描述触发条件、操作清单、何时降级。

### knowledge_gap（知识增强）

**触发**：人+agent 都缺领域知识（notation、标准、领域惯例）。

**操作**：
- knowledge.md 升级为核心活文档：每个产出物类型独立条目，含定义+可运行示例+常见错误+系统映射
- plan 步骤拆 learn→design→verify 微循环；学习步骤可并行
- 隐含 P-K 检查层：能否口头解释？参考了权威例子？理解无内部矛盾？
- 阻塞信号识别：反复改同一元素→回退 knowledge.md，不硬调参数

**何时降级**：参考材料自包含（教材有全部公式+代码）→ knowledge_gap=0，knowledge.md 直接转录。

**无此特征时**：knowledge.md 为普通 Stage 1 输出，写完后冻结。

### needs_overview（静态分解）

**触发**：产出物结构不显然，多模块/多输出物。

**操作**：写入 overview.md，按 cognitive distance 选 1-3 层（见下方 Design Overview 节）。

**无此特征时**：跳过 overview.md。

### 其余特征

其余特征（needs_report / needs_research / has_ambiguity / multi_stage / needs_iteration / needs_parallel / high_stakes / has_artifact）的操作见 Feature Dispatch 表，无需额外展开。

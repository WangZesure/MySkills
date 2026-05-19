---
name: workframe-to-report
description: "从 work_frame 文件升华为结构化论文式报告——明确的文件到章节映射"
version: 1.0.0
category: software-development
---
related_skills: [agent-work-frame, task-type-classification]
category: software-development
---

# Work_Frame → Report 升华方法论

## 何时使用

Stage 6 交付后，所有 P0 testpoints 通过 → 生成 `workspace/REPORT.md`

## 核心映射：work_frame 文件 → 报告章节

```
backward/goal.md ──────────────────→ 1. Abstract (含核心结果)
                                     2. Problem Definition (I/O 表)

backward/testpoints.md ────────────→ 6. Testpoint Verification (P0/P1/P2 表格)
                                     5. Results 的数据来源

forward/knowledge.md ──────────────→ 3. Background / Key Concepts
forward/reference.md ──────────────→ 3. Related Work / Prior Art

runtime/overview.md ───────────────→ 4. Design (架构图、模块分解)
runtime/plan.md ───────────────────→ 4. Method (步骤、依赖、关键决策)

runtime/memory.md ─────────────────→ 7. Agent Collaboration Reflection

workspace/*.py ────────────────────→ 4. Implementation (代码引用)
实际运行日志 ──────────────────────→ 5. Results (性能数据)
```

## 报告章节模板

### 1. Abstract（来源：goal.md）
模板：`本实验[任务一句话]。使用[方法]，在[环境]上完成了[核心指标]。`

### 2. Problem Definition（来源：goal.md I/O 表）
| 项目 | 描述 |
|------|------|
| 输入 | 数据格式、尺寸、来源 |
| 输出 | 期望输出格式、数量 |
| 约束 | 平台限制、不可用工具 |
| 目标 | 量化目标 |

### 3. Background & Related Work（来源：knowledge.md + reference.md）
- **Key Concepts**：从 knowledge.md 提取定义，保留公式编号
- **Prior Art**：从 reference.md 提取参考来源

### 4. Design & Method（来源：overview.md + plan.md + memory.md）
- Architecture：PlantUML 或 ASCII 图
- Module Decomposition：模块树 + I/O
- Key Decisions：为什么选这个方式？遇过什么坑？
- Implementation Steps：从 plan.md 提取

### 5. Results（来源：testpoints.md + 运行日志）
- 输出验证表（每层shape、期望vs实际）
- 性能数据
- ASCII 可视化

### 6. Testpoint Verification（来源：testpoints.md + 实际运行）
| ID | 测试项 | 期望 | 实际 | 状态 |
|----|--------|------|------|------|

### 7. Agent Collaboration Reflection（来源：memory.md）
- 哪些任务委托？为什么？
- 分类决策（参考材料型/知识密集型/计划驱动...）
- 下次怎么改进？

## 升华技巧：不是复制粘贴，是重新叙述

| 框架语言 | 报告语言 |
|---------|---------|
| "TODO: 计算卷积层前向传播" | "通过4重循环实现滑动窗口内积" |
| "P0-5: cat → class 281" | "分类结果为 ID 281 (tabby cat)，置信度 52.5%" |
| "plan.md Step 3 失败" | "实现池化层时遇到步长不匹配，通过...解决" |

框架文件是**笔记**（碎片、面向agent），报告是**叙事**（结构化、面向人）。

## 真实案例

### ICS lab2
`Abstract→goal.I/O→98% | Background→knowledge.定义 | Design→overview.架构 | Testpoints→全部P0通过`

### ICS lab3
`Abstract→VGG19+class281 | Background→Conv/Pool/VGG19 | Results→337s+prob=0.525`

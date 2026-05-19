---
name: task-type-classification
description: "Feature-based task analysis BEFORE filling work_frame — extract task features to determine which framework modules to strengthen. NOT a classification tree: features stack, they don't compete."
version: 2.0.0
category: software-development
---
related_skills: [agent-work-frame, workframe-to-report]
category: software-development
---

# Task Feature Extraction — 填框架前先提取特征

## 触发条件

在创建任何 work_frame 文件之前，先提取任务特征向量。**不贴标签，不分类——任务可以同时触发多个特征，每个特征独立增强对应的框架模块。** 特征叠加，不互斥。

## 特征维度

对每个特征，判 **0（不触发）/ 1（轻度触发）/ 2（重度触发）**。degree ≥ 1 即触发对应增强模块。

| # | 特征 | degree | 含义 | 触发信号（从 prompt 中找） |
|---|------|--------|------|--------------------------|
| F1 | `knowledge_gap` | 0/1/2 | 人+agent 都缺领域知识 | "不熟悉""需要学""这是什么"；agent 检索后确认知识不足 |
| F2 | `needs_overview` | 0/1/2 | 产出物结构值得静态分解 | 多模块/多输出物；架构不一目了然；"架构是什么" |
| F3 | `needs_report` | 0/1 | 最后需要论文式报告 | "出报告"；课程作业；正式交付 |
| F4 | `needs_research` | 0/1/2 | 需查外部参考材料 | 规约不完备；需论文/标准/API 文档；"查一下" |
| F5 | `has_ambiguity` | 0/1/2 | 需求模糊，需先澄清 | prompt 有信息缺口；描述不具体；"大概""类似""可能" |
| F6 | `multi_stage` | 0/1/2 | 有独立子阶段需管理 | 前后阶段 I/O 不同；无法一口气做完；"先做A再做B" |
| F7 | `needs_iteration` | 0/1 | 设计开放，需人工反馈 | "先试试"；结果需人类判断才能推进；"看看效果" |
| F8 | `needs_parallel` | 0/1/2 | 子任务可独立并行 | 多个独立学习/构建任务；无相互依赖；"这几个可以同时做" |
| F9 | `high_stakes` | 0/1 | 错误成本高 | 考试评分；线上发布；不可逆操作 |
| F10 | `has_artifact` | 0/1 | 产出代码/图/文档需自查 | 任何非纯调研的输出（几乎总是=1） |

## 提取流程

```
1. 读 user prompt → 逐个特征扫描触发信号
2. 对每个特征给出 degree + 一句话证据
3. 生成 feature vector（如：knowledge_gap=2, needs_report=1, needs_parallel=1）
4. 对 degree≥1 的特征，列出对应的增强模块（见下方映射表）
5. 将 feature vector 写入 goal.md 顶部或 STATUS.md 首段，供后续 session 复用
```

**不确定时**：degree 保守取 1（宁可多做不遗漏），后续人工纠正后存入 memory。

## 特征 → 增强模块映射

每个特征触发 work_frame 中的一个或多个具体操作。**特征独立触发，叠加生效。**

| 特征触发 | 增强模块 | 在 work_frame 中的具体操作 |
|---------|---------|--------------------------|
| F1 `knowledge_gap` | **知识增强** | knowledge.md 升级为核心活文档；plan 步骤拆 learn→design→verify 微循环；隐含 P-K 检查层 |
| F2 `needs_overview` | **静态分解** | 写入 overview.md，按 cognitive distance 选 1-3 层 |
| F3 `needs_report` | **报告生成** | 执行结束后自动触发 REPORT.md（调用 workframe-to-report） |
| F4 `needs_research` | **外部调研** | 启用 reference.md（append-only）；knowledge.md 标注外部来源 |
| F5 `has_ambiguity` | **澄清闸门** | Stage 2 前插入 clarify gate；不确定的不执行 |
| F6 `multi_stage` | **子阶段管理** | 启用 sections.md + overview-[X].md；每阶段有 I/O 契约 |
| F7 `needs_iteration` | **人工反馈循环** | memory.md 版本递增；每轮追加记录；plan.md 不预设全部步骤 |
| F8 `needs_parallel` | **并行标记** | plan.md 标注并行组；delegate_task / Claude Code 批量调度 |
| F9 `high_stakes` | **验证增强** | testpoints.md 扩大：P0 覆盖所有关键路径；每交付品过验证门 |
| F10 `has_artifact` | **自查步骤** | plan 每步尾追加自查子步骤（对照 spec 或 testpoint） |

## 常见特征组合参考（启发式，非分类）

以下组合是**常见模式**，帮助 agent 快速判断，但**不强制、不互斥**。实际任务的特征向量可以自由组合。

| 常见模式 | 典型特征组合 | 例子 |
|---------|------------|------|
| **知识密集型交付** | knowledge_gap=2 + needs_report + has_ambiguity | 不熟悉的领域标准 + 需要出正式文档 |
| **代码开发** | has_artifact + needs_parallel + (可选 needs_overview) | 多模块实现、重构 |
| **文档/调研** | needs_report + needs_research + (可选 knowledge_gap) | 文献调研、技术报告 |
| **评估验证** | needs_report + high_stakes + has_artifact | 考试评分、合规检查 |
| **快速原型** | has_artifact + needs_iteration | "先做个能跑的看看" |
| **简单任务** | 仅 has_artifact=1 | 单文件修改、明确的小脚本 |

## 常见错误

❌ 看到公式/代码就判为 knowledge_gap=2
✅ 教材已有的公式代码 → knowledge_gap=0，特征只有 has_artifact=1

❌ 强行贴一个标签（"这是知识密集型任务"）
✅ 特征向量可叠加：一个任务可以同时 knowledge_gap=2 + needs_report=1 + needs_parallel=1

❌ 所有任务都触发所有特征
✅ 默认只有 has_artifact=1，其他按需触发。过度触发 = 过度工程

❌ has_ambiguity=2 时不 clarify 就开工
✅ 模糊需求必须先 clarify gate，不确定的设计不要执行

## 真实案例

| 案例 | feature vector | 说明 |
|------|---------------|------|
| ICS lab2 | has_artifact=1, needs_report=1, high_stakes=1 | 教材含完整公式+代码→knowledge_gap=0 |
| ICS lab3 | has_artifact=1, needs_report=1, high_stakes=1, multi_stage=1 | VGG19分类+风格迁移两阶段 |
| LDM 论文调研 | knowledge_gap=2, needs_research=1, needs_report=1, has_ambiguity=1 | 用户不熟悉+需大量外部资料 |
| PA3 UML 8图 | knowledge_gap=2, needs_parallel=1, has_artifact=1, multi_stage=1 | 8图独立可并行+不熟悉UML标准 |
| 修改单文件配置 | has_artifact=1 | 最简单场景 |

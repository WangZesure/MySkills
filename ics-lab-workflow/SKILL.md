---
name: ics-lab-workflow
description: "ICS lab作业完整工作流——环境、框架、提交流程、平台坑、报告生成。承接 agent-work-frame v3 外迁的所有 ICS / Cambricon DLP / 希冀平台 / Educg 自动评测专属材料。"
version: 2.0.0
related_skills: [agent-work-frame, workframe-to-report]
---

# ICS Lab 作业工作流

## 1. 任务分类（填框架前的第一件事）

| 信号 | 分类 | work_frame侧重 |
|------|------|---------------|
| 教材含完整公式+代码 | **参考材料型** | knowledge直接转录，plan线性拆分 |
| 人和agent都缺知识 | **知识密集型** | knowledge为核心活文档，微循环 |
| 需求明确管线已知 | **计划驱动型** | plan+DAG为主 |
| 需外部调研 | **研究型** | reference+knowledge侧重 |

**判别口诀**："人类能口头解释吗？材料自包含吗？" 能+是 → 参考材料型，直接干。

## 2. Work_Frame → 报告

```
backward/goal.md        → Abstract + Problem Definition
backward/testpoints     → Testpoint Verification
forward/knowledge.md    → Background / Key Concepts
forward/reference.md    → Related Work
runtime/plan.md         → Method / Design
runtime/memory.md       → Agent Collaboration
```

**关键：不是复制粘贴，是重新叙述。** 框架是笔记（碎片、面向agent），报告是叙事（结构化、面向人）。

## 3. 平台特点（paas.extrotec.com）

### 环境
- **镜像**: mlu370_ubuntu22.04-for-student:v6.1（通用LLM版）
- **默认Python**: `/opt/py3.10/bin/python3.10`（需自行pip安装numpy等）
- **DLP Python**: `/torch/venv3/pytorch/bin/python`（含pycnnl）
- **LD_LIBRARY_PATH**: DLP需要 `/usr/local/neuware/lib64`

### 必须注意的坑

| 问题 | 表现 | 修复 |
|------|------|------|
| **imageio不可用** | `ModuleNotFoundError: No module named 'imageio'` | 用PIL替代：`Image.open().convert('RGB')` |
| **Image.Resampling不存在** | Pillow 7.x不识别Resampling命名空间 | 用`Image.LANCZOS`（不要`Image.Resampling.LANCZOS`） |
| **cv2不可用** | `ModuleNotFoundError: No module named 'cv2'` | 删除或注释掉import cv2 |
| **scipy.misc.imresize不可用** | scipy.misc模块deprecated | 用PIL的`resize()` |
| **fc6权重索引偏移** | .mat文件中fc6权重在flatten条目(37) | 用`params['layers'][0][idx-1]`加载 |
| **权重格式** | MatConvNet: [H,W,C_in,C_out] | CPU转置`[2,0,1,3]`，DLP转置`[3,0,1,2]` |
| **DLP输入数据** | 需NHWC格式flatten | 不做transpose，直接`reshape([1,H,W,C]).flatten()` |
| **4重循环太慢** | VGG19单次forward ~5.6分钟 | 用im2col优化（加速76~534x） |

### SSH操作指南
- 本地没有sshpass → 用`SSH_ASKPASS` + `execute_code`的subprocess方式
- 上传文件：base64编码后 `echo | base64 -d > remote_path`
- 后台任务：`nohup python -u script.py > log 2>&1 &`（需Popen不等待）
- scp有时会超时 → 用base64管道更可靠

## 4. 提交流程
1. 代码写好 → 本地打包zip
2. 提交到 `course.educg.net` → 在线作业
3. 根据错误信息修 → 重提交
4. 常见错误：imageio/PIL版本/路径问题居多数

## 5. 三实验关键文件

| 实验 | 提交文件 | 重点 |
|------|---------|------|
| 3.1 CPU | `__init__.py, layers_1.py, layers_2.py, vgg_cpu.py` | Conv/Pool前向4重循环 |
| 3.2 DLP | `__init__.py, vgg19_demo.py` | pycnnl API，无flatten |
| 3.3 风格迁移 | `__init__.py, layers_1.py~3.py, exp_3_3_style_transfer.py, output.jpg` | im2col优化+加速比 |

## 6. Lab3 技术要点
- **VGG19结构**: 16conv + 5pool + 3fc + softmax，所有conv K=3/P=1/S=1
- **卷积前向**: input_pad做padding → 4重循环内积+偏置，或用im2col矩阵乘法
- **池化前向**: 4重循环取窗口max，记录max位置用于反向传播
- **卷积反向**: 旋转权重180°后做full卷积，或用im2col矩阵梯度反传
- **风格迁移**: ContentLoss(C×H×W的MSE) + StyleLoss(Gram矩阵差异) + Adam优化器
- **im2col**: 展开输入为列矩阵→权重矩阵乘→col2im还原，加速76~534x

## 7. 附属材料索引

以下文件由 `agent-work-frame` v2 → v3 迁移至本 skill。深入坑点查这里：

### references/
- `ics-platform-submission.md` — Lab2 在希冀平台的 pickle 协议、import 路径、CWD 探针
- `ics-lab3-v6.1-quirks.md` — Lab3 v6.1 镜像路径变化、缺 NumPy、cv2 dead import、imageio 替代
- `ics-lab3-style-transfer.md` — Lab3 3.3 Conv/Pool 反向、ContentLoss/StyleLoss、训练循环
- `pycnnl-dlp-platform-quirks.md` — Cambricon DLP / pycnnl API、权重格式、NHWC flatten
- `platform-autograding-pitfalls.md` — Educg 自动评测 zip 结构、import 路径、batch_size 陷阱、HIDDEN 导出
- `im2col-convolution-optimization.md` — CPU 卷积 im2col 优化（加速 76~534x）

### scripts/
- `convert_npy_protocol2.py` — 跨版本 NumPy 权重转换（Python 3.10+ → Python 3.7 / NumPy 1.19，pickle protocol 2）

### 跨场景通用条目（保留在 agent-work-frame）
- SSH 非交互执行（`SSH_ASKPASS` + base64 传输）
- NumPy `.npy` pickle 协议跨版本兼容的原理

# 点调研案例：扩散模型上加"图→条件"子网络

> 完整复现一次"由近到远"调研，展示每层怎么放宽、怎么定位空白。

## 第 0 步：形式化 idea

- 一句话：在训练好的 diffusion 上加一个子网络，输入图片/图片 embedding，输出 clinical factors。
- 组件拆解：① 子网络（图→条件）② 冻结主扩散模型 ③ loss1=对齐手工提取的条件（软教师）④ loss2=重建。

## 第 1 层（全部组件保留）

查询：`all:"condition" AND all:"consistency" AND all:"extract" AND all:"diffusion" AND cat:cs.CV` 等组合。

结果：没有完全一致的论文 → 记录断档（这本身是新颖点信号）。

## 第 2 层（去掉"对齐手工条件"组件，保留"子网络+冻结主网+双损失"）

查询：`all:"encoder" AND all:"condition" AND all:"latent" AND all:"diffusion" AND all:"decoder"`。

命中 ★★★：**LISA（arXiv:2606.27192）**——"训练 side network 编码视觉条件、融合进冻结预训练主网络"，损失 = 扩散损失 + 正则项。结构性命中。抓全文摘要确认（它的正则项对齐"似然分数"，不是临床因子——差异即我们的新颖点）。

## 第 3 层（只保留"图→条件编码器 + 扩散重建"）

命中：**Diffusion Autoencoders（2203.11326）**（gh_grep 确认 Stability-AI 有实现）、MoRAE。

## 第 4 层（只保留主题域）

命中：IP-Adapter / ControlNet / T2I-Adapter（成熟 adapter 范式）；Anchoring-and-Steering（条件忠实度）。

## 空白定位

```
我们的做法 = LISA 骨架（side network + 冻结主网 + 双损失）
           + 临床可测量条件（HSV/mask，非视觉 token）
           + loss1 = 手工提取因子当软教师（LISA 对齐的是似然分数，无人用临床测量当教师）
```

→ 新颖点：**"手工提取的临床测量作为教师信号监督条件子网络"**在文献中不存在。

## 经验

- 每层查询都要换关键词族（同义词 + 去掉组件），单次查询命中 0 不代表方向不存在；
- 429 限流是常态：退避 + 串行 + 间隔，别并行打 arXiv；
- 命中后必须抓摘要验证，标题相关 ≠ 机制相关。

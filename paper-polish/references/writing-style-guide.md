# Academic Paper Writing Style Guide

基于导师对论文abstract的修改模式总结。在撰写或修改学术论文时遵循以下规范。

---

## 一、核心原则

### 1. 用词精确，避免过度表述 (Avoid Overstatement)

学术写作需要自信但不夸大。以下词语需要警惕：

| 避免 | 替代 | 原因 |
|------|------|------|
| critical (importance/role) | important, essential | "critical"过于戏剧化 |
| unique | distinct, specific | 很少有东西是真正"unique"的 |
| extreme(ly) | substantial, considerable | 过度夸张 |
| severe(ly) | substantial, marked | 同extreme |
| fundamental(ly) | 删掉或改为 core, key | 导师从abstract中删除了"fundamental" |
| cornerstone | established, important | 过于修辞化 |
| remarkable | strong, notable | 让结果自己说话 |

**例外情况**：
- "critical role in cancer staging" — 在医学语境中描述确实关键的临床角色时可保留
- "severe class imbalance" — ML领域的标准术语，可保留

### 2. 简化嵌套结构 (Simplify Nested Structures)

导师在修改abstract时删除了 `(1)...(2)...` 的枚举结构。在正文中：

- **不要让读者在脑海中维护一个编号列表**。改为独立的句子或自然段落。
- **避免括号中再嵌套括号**，尤其是括号内含完整句子+引用的情形。

❌ 差：
```
due to two fundamental sources of variability: (1) clinical confounding factors, including...; and (2) the morphologically diverse and partially unknown spectrum of malignant cells...
```

✅ 好：
```
due to clinical confounders, including..., together with the broad morphological diversity and partially unknown phenotypes of malignant cells.
```

### 3. 精炼冗长表述 (Tighten Verbose Phrases)

删除不必要的修饰语和重复描述。

❌ 差：
```
comprising whole slide images acquired over an eight-year acquisition window (2017--2025) within a single clinical institution, with binary patch-level labels
```

✅ 好：
```
which was collected over eight years, with binary patch-level annotations
```

### 4. 删除冗余和说教式结尾 (Remove Redundancy & Editorializing)

- 不要在总结段重复前文已经说过的内容
- 不要以"particularly in resource-limited settings where expert pathologists are scarce"这类说教式表述结尾——导师从abstract中明确删除了这类内容

### 5. 精确区分"显著"的含义 (Distinguish "significantly" vs "consistently")

- `significantly outperforms` → `consistently outperforms`（当你想表达"在各种条件下都更好"而非统计显著性时）
- 仅在明确有统计检验结果时才使用"significantly"
- 描述你自己的方法优势时，用"consistently"比"significantly"更严谨

---

## 二、语言规范

### 1. 避免口语化/非正式表达

| 避免 | 替代 |
|------|------|
| naive (形容方法/系统) | unsophisticated, 或改为从句 "that lack clinical context" |
| easily be misinterpreted | may be misinterpreted |
| flag (作为动词) | identify (ML领域可酌情保留) |
| struggle with | are challenged by, are limited by |
| suffering from | exhibiting, with (拟人化在学术写作中应避免) |
| liable to | likely to, tends to |
| problematic | consequential, challenging |
| deficiency (形容方法缺陷) | limitation |
| only (带主观色彩，如"only F1 0.185") | 直接陈述数字，让数据自己说话 |
| disentangle | ML领域标准术语，可保留 |
| nuisance variation | 统计学标准术语(nuisance variable)，可保留 |

### 2. 避免拟人化 (Avoid Anthropomorphism)

方法/模型不会"suffer"、"struggle"、"learn to understand"。使用客观描述。

❌ `Methods suffer under staining variation`  
✅ `Methods perform worse under staining variation`

### 3. 英美拼写一致性 (British vs American Spelling)

**全文必须统一为一种拼写体系。** 导师使用的倾向英式拼写：

- `colour` 非 `color`
- `normalisation` 非 `normalization`
- `characterised` 非 `characterized`
- `visualises` 非 `visualizes`
- `behaviour` 非 `behavior`
- `localisation` 非 `localization`
- `multi-centre` 非 `multi-center`
- `generalisability` 非 `generalizability`
- `maximising` 非 `maximizing`

### 4. 时态一致性 (Tense Consistency)

- 描述自己的方法/贡献：**现在时** (`We propose`, not `We proposed`)
- 描述实验过程/结果：过去时
- 描述表格/图表内容：现在时

---

## 三、句式结构

### 1. em-dash 打断主句

em-dash (--- ) 插入的补充说明不应该让读者忘记主句的主语和谓语是什么。

❌ `X is a viable---and in the case of Y, more robust---strategy for Z.`  
✅ `X is a viable strategy for Z. In the case of Y, it is the more robust choice.`

### 2. 括号引用不要嵌套在关系从句中间

这是最常见的可读性杀手。

❌：
```
Diagnostic features such as X, which are themselves Y and would be Z (some fact with citation), are thus left intact.
```
主语"Diagnostic features"和谓语"are thus left intact"之间隔了3行，读者必须反复回读。

✅：
```
Diagnostic features such as X are themselves Y and would be Z, yet are left intact under conditioning---an important property given that [the parenthetical fact]~\cite{...}.
```

### 3. 逻辑一致性

- `dichotomy`（二分法）只能有两个选项。如果有三个，用 `choice` 或 `alternatives`。
- 不要用 `dichotomy between A and B, with a third option C` 这种结构。

❌ `replacing the conventional dichotomy between A and B with a third option: C`  
✅ `replacing the conventional choice between A and B with a third approach: C`

### 4. 句子长度

- 如果一句话超过4行，考虑拆分
- 结论段如果全段只有一句话，必须拆分
- 好的学术写作：核心论点短句 + 补充说明中句

---

## 四、自查清单 (Checklist)

修改完论文后逐项检查：

- [ ] 搜索 `critical` `unique` `extreme` `severe` — 是否每一个都经得起推敲？
- [ ] 搜索 `significantly` — 是否有统计检验支撑？否则改为 `consistently` 或 `substantially`
- [ ] 搜索 `color` / `colour` — 全文统一了吗？
- [ ] 搜索 `normalization` / `normalisation` — 全文统一了吗？
- [ ] 搜索 `suffer` `struggle` `flag` `naive` `liable` `problematic` — 是否过于口语化？
- [ ] 检查是否有 `(1)...(2)...(3)` 嵌套在句子中的枚举 — 可以拆成独立句吗？
- [ ] 检查是否有括号内包含完整句子+引用的情形 — 可以移到句末吗？
- [ ] em-dash插入语是否打断了主句的主谓结构？
- [ ] 结论段是否用现在时描述自己的方法？
- [ ] 结尾是否避免了"particularly in resource-limited settings"式的说教？
- [ ] `dichotomy` 是否真的只有两个选项？
- [ ] 是否有"only F1 X"这类主观措辞 — 让数据自己说话

---

## 五、导师修改模式的本质

导师的修改不是风格偏好，而是指向一个统一的写作哲学：

1. **尊重读者**：不要让读者在复杂嵌套结构中迷失，不要让读者替你判断"critical"或"unique"
2. **精确高于华丽**：用词准确比用词漂亮更重要
3. **简洁高于全面**：删掉不会损失信息的词句，比保留它们更好
4. **让贡献自己说话**：删除冗余总结和说教，实验数据本身就是最好的论证

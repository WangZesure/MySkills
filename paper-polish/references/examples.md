# Before/After Examples

Real examples from an academic paper revision, based on an advisor's edits.

---

## Overstatement

**Before:** `Serous effusion cytopathology is a critical minimally invasive diagnostic modality...`
**After:** `Serous effusion cytopathology is an important minimally invasive technique...`

**Before:** `...due to two fundamental sources of variability...`
**After:** (removed — "fundamental" cut)

**Before:** `...presents unique challenges that distinguish it from other medical imaging tasks.`
**After:** `...presents distinct challenges that distinguish it from other medical imaging tasks.`

**Before:** `...morphological diversity of malignant cells is extreme and partially unknown.`
**After:** `...morphological diversity of malignant cells is substantial and partially unknown.`

**Before:** `Ablation studies confirm the critical importance of clinical factor conditioning...`
**After:** `Ablation studies confirm the importance of clinical factor conditioning...`

**Before:** `...degrade on morphologically complex regions and extreme staining conditions.`
**After:** `...degrade on morphologically complex regions and challenging staining conditions.`

---

## Precise Claims

**Before:** `...significantly outperforms representative unsupervised anomaly detection baselines...`
**After:** `...consistently outperforms representative unsupervised anomaly detection methods...`

**Before:** `...substantially outperforms five unsupervised baselines.`
**After:** `...consistently outperforms five unsupervised methods.`

---

## Nested Structures

**Before (enumeration in running text):**
```
Specifically, we extract three types of clinical factors from each slide---
morphological region, staining characteristics, and erythrocyte appearance---
which are represented as three conditioning tokens and two spatial masks:
(1) the morphological region, capturing the spatial location...;
(2) staining characteristics captured through colour distribution statistics;
and (3) erythrocyte appearance quantified through morphological features.
```
**After (flowing prose):**
```
Specifically, we extract three types of clinical factors from each slide---
morphological region, staining characteristics, and erythrocyte appearance---
which are represented as three conditioning tokens and two spatial masks.
The morphological region token captures the spatial location of the patch
within the smear (Edge, Body, or Head). Staining characteristics and
erythrocyte appearance are captured through colour distribution statistics
and morphological features, respectively, and each is encoded as both a
conditioning token and a spatial mask.
```

**Before (em-dash interrupting subject-verb):**
```
Our results demonstrate that encoding...is a viable---and in the case of
Wright--Giemsa-stained cytology, more robust---strategy for unsupervised
anomaly detection.
```
**After (split into two sentences):**
```
Our results demonstrate that encoding...is a viable strategy for
unsupervised anomaly detection. In the case of Wright--Giemsa-stained
cytology, it is the more robust choice.
```

**Before (citation buried in relative clause):**
```
Diagnostic features such as nuclear hyperchromasia and chromatin granulation,
which are themselves staining-dependent and would be attenuated by aggressive
normalisation (degenerative nuclear hyperchromasia is itself a documented
cause of false-positive interpretation [cite]), are thus left intact under
conditioning.
```
**After (citation moved to end, parenthetical integrated):**
```
Diagnostic features such as nuclear hyperchromasia and chromatin granulation
are themselves staining-dependent and would be attenuated by aggressive
normalisation, yet are left intact under conditioning---an important property
given that degenerative nuclear hyperchromasia is a documented cause of
false-positive interpretation [cite].
```

---

## Informal Language

**Before:** `These technical artifacts can easily be misinterpreted as anomalies by naive detection systems.`
**After:** `These technical artifacts may be misinterpreted as anomalies by detection systems that lack clinical context.`

**Before:** `...achieving high performance on known tumor types but suffering from poor generalization...`
**After:** `...achieving high performance on known tumor types but with limited generalization...`

**Before:** `...but still require substantial labeled abnormal data and struggle with the long-tail distribution...`
**After:** `...but still require substantial labeled abnormal data and are challenged by the long-tail distribution...`

**Before:** `...which, without explicit conditioning, is liable to be scored as anomalous.`
**After:** `...which, without explicit conditioning, is likely to be scored as anomalous.`

**Before:** `This common deficiency motivates...`
**After:** `This common limitation motivates...`

**Before:** `...our method attains only F1 0.185...`
**After:** `...our method attains F1 0.185...`

**Before:** `...condition on them.`
**After:** `...explicitly modelling them as conditioning variables.`

---

## Logic Errors

**Before:** `...replacing the conventional dichotomy between "normalise away the confounders" and "ignore the confounders" with a third option: condition on them.`
**After:** `...replacing the conventional choice between normalising away confounders and ignoring them with a third approach: explicitly modelling them as conditioning variables.`
*(A dichotomy = exactly two; "third option" breaks the word. Also "condition on them" is too informal.)*

---

## Spelling Consistency

The paper used `color` in the Introduction but `colour` in the Method section.
Standardized all to British `colour`, `normalisation`, etc.

**Exception:** `\textcolor{red}` (LaTeX command) must NOT be changed.

---

## Tense

**Before:** `We proposed Clinical Diffusion...`
**After:** `We propose Clinical Diffusion...`
*(Present tense for describing your own method.)*

---

## Redundancy & Verbosity

**Before:**
```
We introduce the first publicly available benchmark dataset for serous
effusion cytopathology anomaly detection, comprising whole slide images
acquired over an eight-year acquisition window (2017--2025) within a single
clinical institution, with binary patch-level labels and standardized
evaluation protocols.
```
**After (in abstract):**
```
...which was collected over eight years, with binary patch-level annotations
and standardized evaluation protocols.
```

**Before (abstract ending):**
```
Our approach shows strong potential for alleviating the diagnostic burden
in clinical cytopathological screening, particularly in resource-limited
settings where expert pathologists are scarce.
```
**After:**
```
...showing strong potential for alleviating the diagnostic burden in
clinical cytopathological screening.
```
*(The "resource-limited settings" clause was cut as editorializing.)*

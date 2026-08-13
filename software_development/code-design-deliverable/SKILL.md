---
name: code-design-deliverable
description: "From a problem description to a professional code deliverable with full engineering documentation — design, implement, analyze, test, profile, report, and package."
version: 1.0.0
created_by: agent
---

# Code Design Deliverable

From a problem description to a professional code deliverable — design, implement, analyze, test, profile, report, and package.

## When to Use

- User gives a programming/algorithm/design problem description (often via PPT or doc)
- Task requires: implementation + code analysis + unit tests + performance profiling + written report
- Deliverable: source code + test suite + performance data + PDF report + ZIP

## Pipeline Overview

```
Problem/Requirement (PPT/text)
  │
  ├── 1. Problem Analysis + Design     → multiple algorithm comparison, strategy selection
  ├── 2. Implementation                → Python, PEP 8, type annotations, docstrings
  ├── 3. Static Code Analysis          → pylint (target ≥ 9.0)
  ├── 4. Unit Testing                  → unittest, boundary + error coverage
  ├── 5. Performance Profiling         → timeit multi-scale comparison + cProfile hot-spot
  ├── 6. Exception Handling            → hierarchical exception classes
  ├── 7. Report Generation             → HTML → PDF (WeasyPrint, 9 required dimensions)
  └── 8. Package Delivery              → source + tests + data + perf script + report + ZIP
```

---

## Step-by-Step Workflow

### 1. Problem Analysis & Design

Extract the core problem from input. Create a comparison table:

| Method | Function | Time Complexity | Space Complexity | Trade-off |
|--------|----------|----------------|-----------------|-----------|
| Brute-force | `brute_force` | O(n·k) | O(1) | Simple, slow on large n |
| Optimal | (e.g. deque) | O(n) | O(k) | Best for large n |
| Alternative | (e.g. heap) | O(n log k) | O(k) | Middle ground |

**Design decisions to document:**
- Why this optimal method is chosen
- Strategy pattern for runtime method switching
- Unified entry point signature

### 2. Implementation Guidelines

#### Coding Standards
- **Style:** PEP 8 — enforced via pylint
- **Docstrings:** Google style
- **Type annotations:** PEP 484 — full coverage on all function signatures
- **Naming:** `snake_case` for functions/vars, `CapWords` for classes, `UPPER_CASE` for constants

#### File Structure
```
project/
├── main_module.py           # Core implementation
├── test_main_module.py      # Unit tests (20+ cases)
├── test_data.json           # Test data (small + large)
├── perf_analysis.py         # Performance profiling script
├── report.html              # Report source (→ PDF)
└── output/
    └── 题目_作业报告.pdf     # Final PDF
```

#### Unified Entry Point
```python
def solve_problem(data, params, method='optimal'):
    """Unified entry with runtime strategy switching."""
```

### 3. Static Code Analysis (pylint)

**Target:** Score ≥ 9.0/10

**Checklist:**
- [ ] All imports at top level (no lazy imports in function bodies)
- [ ] Module-level docstring present
- [ ] All public functions have docstrings
- [ ] Variable naming consistent
- [ ] No unused imports or variables

```bash
pylint main_module.py
```

### 4. Unit Testing (unittest)

**Coverage requirements:**

| Category | Min cases | Examples |
|----------|-----------|---------|
| Normal functionality | 4+ | Standard input, edge k values |
| Boundary conditions | 4+ | k=1, k=len, single element, empty? |
| Error / invalid input | 6+ | Empty array, k≤0, k>len, None, type error, unknown method |
| Cross-validation | 4+ | All methods produce identical results |

**Structure:**
```python
class TestNormalFunction(unittest.TestCase): ...
class TestBoundaryCases(unittest.TestCase): ...
class TestErrorInputs(unittest.TestCase): ...
class TestCrossValidation(unittest.TestCase): ...
```

**Run:** `python -m unittest test_main_module.py -v`

### 5. Performance Profiling

#### Multi-scale Comparison (timeit)

Compare across data sizes. Template:

| n | k | Brute-force | Deque | Heap | Speed-up |
|---|---|-------------|-------|------|----------|
| 100 | 10 | 0.029ms | 0.017ms | 0.020ms | 1.68× |
| 5,000 | 200 | 22.5ms | 0.90ms | 0.99ms | 25× |
| 50,000 | 1,000 | 1.20s | 10.2ms | 13.1ms | 118× |

**Also analyze:** Window size (k) impact at fixed n.

#### Hot-spot Analysis (cProfile)

```python
import cProfile, pstats
cProfile.run('function(args)', 'profile_stats')
p = pstats.Stats('profile_stats')
p.sort_stats('cumtime').print_stats(10)
```

### 6. Exception Handling

Design a hierarchical exception system:

```python
class Error(Exception):           # Base
class InvalidInputError(Error):   # Invalid input
class EmptyArrayError(Error):     # Empty input
class OutOfRangeError(Error):     # Parameter out of range
class TypeError(Error):           # Wrong type
class ValueError(Error):          # Wrong value
```

Validate all inputs at entry point before computation.

### 7. Report Generation (9 Required Dimensions)

| # | Dimension | What to cover |
|---|-----------|---------------|
| a | Coding standards | Which standard? How checked? Score? |
| b | Extensibility | What was extended? Future extensions? |
| c | SRP | Single-responsibility: reusable, closed parts |
| d | OCP | Where can new functionality be added without modifying existing code? |
| e | Exception handling | Hierarchy, handling per scenario |
| f | Performance | Complexity, multi-scale table, cProfile, optimization |
| g | Unit testing | Count, pass rate, coverage %, test case table |
| h | Bug report | 0 open defects or known limitations |
| i | File manifest | All delivered files with descriptions |

#### PDF Generation (WeasyPrint)

```bash
# Install fonts (Ubuntu/WSL)
sudo apt-get install fonts-noto-cjk poppler-utils

# In HTML CSS:
# body { font-family: "Noto Sans CJK SC", "SimSun", "Microsoft YaHei", serif; }
# @page { size: A4; margin: 2.5cm 2cm; }

# Compile:
weasyprint report.html deliverable_report.pdf

# Verify Chinese rendering:
pdftotext -layout deliverable_report.pdf - | wc -m
```

### 8. Package & Delivery

```python
import zipfile, os
files = ["main_module.py", "test_main_module.py", "test_data.json",
         "perf_analysis.py", "deliverable_report.pdf"]
with zipfile.ZipFile("交付包.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        if os.path.exists(f): z.write(f, f)
```

---

## Quality Gates

- [ ] pylint ≥ 9.0
- [ ] All unit tests pass (100%)
- [ ] Error inputs handled (no crashes)
- [ ] Cross-validation: all methods produce identical results
- [ ] PDF renders Chinese correctly (verify with pdftotext)
- [ ] ZIP package contains all required files

## Pitfalls

- **WeasyPrint + CJK fonts:** Without `fonts-noto-cjk`, Chinese shows as boxes. Always install fonts before PDF generation. Verify with `pdftotext`.
- **pylint lazy imports:** Move all `import` to top level for max score.
- **Performance noise:** Run each test multiple times (`timeit(..., number=100)`) for stable averages.
- **Test data size:** Large random data can produce big JSON files. Use `random.seed()` for reproducibility.

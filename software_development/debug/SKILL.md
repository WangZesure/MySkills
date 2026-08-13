---
name: ics-debug
description: Structured, data-flow-driven debugging methodology for complex layered software stacks. Covers 5 generalized patterns—regression, missing data, protocol mismatch, performance, and crash/exception—with concrete NEMU/ICS emulator case studies. Also covers opcode analysis and data-flow tracing for the x86 emulator. Use for any multi-layer debugging where data must traverse many modules before producing output.
---

# Stack Debugging Methodology

> **核心原则：跟着数据走 (Follow the data flow)**
> 不要猜，不要地毯式排查。画出数据从源头到目标的每一步，插桩验证每一跳，断点就是 bug 所在。

## Quick Start — Generic Workflow

When facing a bug in any multi-layer system:

1. **Classify** — which of the 5 patterns below does it match?
2. **Map the data flow** — draw the full path from source (input/hardware) to symptom (output/UI)
3. **Instrument at midpoints** — insert logs/checkpoints at each hop, binary-search to find the break
4. **Fix at the breakpoint** — the first hop where data is wrong is where the bug lives

```
Source → [hop1] → [hop2] → ... → [hopN] → Symptom
   ↑        ↑        ↑              ↑
   └── Log  └── Log  └── Log  └── Log ← who has the right data, who doesn't?
```

---

## 5 Generalized Bug Patterns

Each pattern below is presented: **Generic Form** → **ICS Case Study** → **Key Takeaway**.

---

### Pattern A: Regression — "Something that worked is now broken"

**Generic form**: Feature X worked before a code change, but not after.

**Method**:

```
git diff <last-good-ref> -- <suspected-module>/
  │
  ▼
Identify every changed line along the data path
  │
  ▼
Instrument the entry point of each changed module
  │
  ▼
Confirm data arrives → check routing → fix
```

Key question at each step: *"Does the data get to where it should be?"*

**ICS case — VGA black screen**:
- Change from PA3→PA4: `paddr_write` was refactored to write to `pmem` directly
- But VGA device reads from `mmio_space_pool` — data went to the wrong memory region
- Fix: add `is_mmio()` routing before the `memcpy(pmem)` fallback

**Takeaway**: When a change touches a routing/switch point (which path data takes), verify every branch. The data didn't disappear — it went to the wrong place.

---

### Pattern B: Missing / Empty — "The data is null or zero-length"

**Generic form**: A downstream consumer receives empty, zero, or null data from its source.

**Method**: Trace the dependency chain backward from the symptom. At each step ask: *"What upstream value causes this downstream result?"*

```
Symptom (empty output)
  ↑ What feeds this?
Value X
  ↑ Where does X come from?
Source function F
  ↑ What determines F's output?
Upstream data Y  →  check Y's value → is Y null/zero?
```

**ICS case — Menu has no text**:
- Symptom: PAL menu shows background but no text
- Trace: text → `word.dat` → `fs_read` → `file_table[fd].size` → `_fstat` → `st_size = 0` (hardcoded!)
- Fix: `st_size = _lseek(fd, 0, SEEK_END)` instead of a literal 0

**Takeaway**: Empty output rarely means "nothing happened" — it means "someone sent zero bytes upstream". Find who decides the size/length.

---

### Pattern C: Protocol / Interface Mismatch — "Bytes cross a boundary wrong"

**Generic form**: Data is present and correct at sender, but the receiver misinterprets or drops it.

**Method**:

```
SENDER: write bytes → function return → length value
                              │
                              ▼
RECEIVER: read bytes → parse → interpret
                              │
                              ▼
Verify every byte at the boundary:
  - Is the length exactly what the receiver expects?
  - Does the API return value mean "bytes written" or "bytes intended"?
  - Does the encoding match (string vs binary, null-terminated vs length-prefixed)?
```

**ICS case — Keyboard unresponsive**:
- `snprintf(evt_buf, ...)` returns "total chars that would have been written" (including `\0`)
- That value (11 instead of 10) was used as the event length → trailing null byte corrupted parsing
- Fix: `evt_len = strlen(evt_buf)`

**Takeaway**: Cross-layer boundaries are the most common bug source. Every API with a return value needs its semantics verified. One byte of difference in a length field breaks everything downstream.

**Other real examples**:
- HTTP APIs: `Content-Length` vs actual body bytes
- Serialization: struct packing/padding across different compilers
- Network protocols: big-endian vs little-endian wire format

---

### Pattern D: Performance Degradation — "It suddenly got slow"

**Generic form**: Functionality is correct, but execution is 10x–100x slower than expected.

**Method**:

```
1. Check configuration/feature flags FIRST (not code logic)
2. Common culprits:
   - Debug/tracing macros enabled in production
   - Synchronous wait/handshake turned on
   - Polling rate set too high
   - Log level set to DEBUG
3. If config is clean, profile: which function dominates CPU time?
```

**ICS case — PAL runs at <1 fps**:
- `common.h`: `#define DIFF_TEST` was active
- NEMU was comparing every single instruction against QEMU via GDB → ~100x slowdown
- Fix: comment out `#define DIFF_TEST`

**Takeaway**: Performance problems are nearly always a configuration or measurement artifact first. Check the knobs before profiling the code.

---

### Pattern E: Crash / Exception — "Invalid operation or unhandled case"

**Generic form**: A dispatch table, state machine, or type switch hits an unhandled code path.

**Method**:

```
Error signal (invalid opcode, segfault, 404, 500)
  │
  ▼
Decode the error:
  - What value triggered it? (opcode byte, HTTP method, enum value, protocol message type)
  - Where is the dispatch table that handles this type?
  - Is the entry EMPTY/UNIMPLEMENTED/NOT_FOUND?
  │
  ▼
If missing → implement the handler (consult spec/manual/API docs)
If present → check if the handler has a logic bug
```

**ICS case — Invalid opcode during PAL save/battle**:
- Crashing opcodes: `C1 05` (group instruction, ext_opcode 0 = ROL) and `0F AC` (two-byte = SHRD)
- Both were `EMPTY` in the opcode table → not implemented
- Fix: read i386 manual, implement the instruction

**Takeaway**: "Unhandled X" errors mean the dispatch table has a hole. Find the table, fill the hole. Don't try to fix the symptom at the caller — the table IS the source of truth.

**Other real examples**:
- HTTP 405 Method Not Allowed → allowed_methods list missing the verb
- JSON parse error → edge case in the format not handled
- Switch statement `default: assert(0)` → unplanned enum value
- Undefined opcode/handler → missing implementation

---

## Generalized Debugging Techniques

### 1. Checkpoint/Instrumentation Bisect

Insert observation points at strategic layers of the stack:

```
_halt(1) or Log("ENTER: module A")    → check 1
_halt(2) at layer 2 boundary           → check 2
_halt(3) at end of processing pipeline  → check 3
```

- If check 1 passes but check 2 never fires → bug is between them
- Different checkpoint IDs (`_halt(N)` with different N) identify paths without reading log content

### 2. Data-Flow Map

Draw the complete data path for ANY multi-layer system:

```
Input Device / User / Sensor
  └→ Layer 1 (transport/driver/decoder)
       ├→ Routing/Switch (which path?)
       └→ Layer 2 (processing/transform)
            └→ Layer 3 (output/render/response)
                 └→ User experience / Symptom
```

Add annotations at every hop:
- What format/type is the data at this point?
- Which function/API transforms it?
- What conditions route it one way vs another?

### 3. Binary Search on the Data Path

Instead of reading all layers linearly, check the middle layer first:

```
Layer checkpoint: does data arrive here correctly?
  YES → bug is downstream (closer to output)
  NO  → bug is upstream (closer to source)
```

Repeat the bisection until the breakpoint is isolated to one function.

---

## When to Use Class-Specific Sub-Skills

This skill provides the **generic methodology**. For stack-specific details, load:

| Stack Environment | Load Skill | What It Adds |
|---|---|---|
| x86 emulator / NEMU | `ics-debug` (REFERENCE.md) | Opcode tables, NEMU data-flow maps, common pitfalls |
| Web stack (frontend→API→DB) | — (pattern B/C/D apply directly) | Follow HTTP request/response body, check Content-Type |
| Embedded / firmware | — (pattern A/E apply directly) | Check pin routing, register map, interrupt vector table |
| Compiler / interpreter | — (pattern E applies directly) | Check IR node types, symbol table lookups, lowering passes |

> **Rule of thumb**: The 5 patterns above handle ~90% of multi-layer debugging. The ICS-specific reference (REFERENCE.md) is an example of how to document a particular stack. Follow that template for your own stack.

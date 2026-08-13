# NumPy Pickle Cross-Version Compatibility

When a `.npy` file saved with NumPy on Python 3.8+ (pickle protocol 5) needs to be loaded by NumPy on Python 3.7 (pickle protocol 4 max), the default `np.save()` format breaks.

## Symptom

```
_pickle.UnpicklingError: pickle data was truncated
```

## Root Cause

- Python 3.8+ defaults to pickle protocol 5
- Python 3.7 only supports pickle protocol ≤ 4
- `np.save(dict, allow_pickle=True)` uses Python's default pickle protocol

## Quick Fix

Run the bundled conversion script (protocol 2, compatible with Python 2.7+ / NumPy 1.19+):

```bash
python scripts/convert_npy_protocol2.py <input.npy> [output.npy]
```

This script is already included in the `agent-work-frame` skill at `scripts/convert_npy_protocol2.py`. It reads the weight, re-pickles with protocol 2, rebuilds the `.npy` header, and verifies the result.

## Manual Recipe (for reference)

```python
import numpy as np, pickle, struct

# Load original weight
p = np.load("weight.npy", allow_pickle=True).item()

# Wrap in 0-d array (mimics np.save behavior — REQUIRED for .item() compatibility)
arr = np.empty((), dtype=object)
arr[()] = p

# Pickle with protocol 2
buf = pickle.dumps(arr, protocol=2)

# Rebuild .npy file manually
header = b"{'descr': '|O', 'fortran_order': False, 'shape': (), }"
pad = (16 - (10 + len(header)) % 16) % 16
header += b" " * pad + b"\n"

with open("weight_compat.npy", "wb") as f:
    f.write(b"\x93NUMPY\x01\x00")
    f.write(struct.pack("<H", len(header)))
    f.write(header)
    f.write(buf)

# Verify with .item()
loaded = np.load("weight_compat.npy", allow_pickle=True).item()
```

## Critical Detail: 0-d Array Wrapping

If you pickle the dict directly (without wrapping in a 0-d array), `np.load()` returns the dict directly — breaking code that calls `.item()`:

```python
# WRONG: np.load returns dict, .item() fails
buf = pickle.dumps(p, protocol=2)  # p is a plain dict

# RIGHT: np.load returns 0-d array, .item() extracts dict
arr = np.empty((), dtype=object); arr[()] = p
buf = pickle.dumps(arr, protocol=2)
```

## Pitfalls

- Protocol 2 is safe for Python 2.7+ but produces larger files than protocol 5
- The manual .npy header rebuild must match the original format exactly
- `np.save()` creates a 0-d object array containing the dict, not a dict directly — this is why `.item()` works
- This issue commonly surfaces in Chinese university ICS/MLU course environments running Python 3.7 + NumPy 1.19 on Cambricon DLP platforms

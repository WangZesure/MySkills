# Platform Auto-Grading Pitfalls (ICS / Educg Course Platform)

Common submission format requirements and silent failure modes on the ICS auto-grading platform.

## Zip Structure

Files are extracted into `stu_upload/` directory. The zip must contain files at root level:

```
exp_N_M.zip
├── __init__.py
├── layers_1.py
├── mnist_mlp_cpu.py
├── mnist_mlp_demo.py     # 2.2 only
└── weight.npy            # 2.2 only
```

Platform places them at: `/cg/exp_N_M/stu_upload/xxx.py`

## Import Paths

Since files go into `stu_upload/`, use: `from stu_upload.layers_1 import ...`

NOT `from layers_1 import ...` (fails with ModuleNotFoundError).

## MNIST Data Path

Platform puts data at `../mnist_data/` (one level above experiment dir):

```
/cg/
  exp_2_1_mnist_mlp/       ← CWD when main_exp_2_1.py runs
    stu_upload/...
  mnist_data/               ← train-images-idx3-ubyte etc.
```

Use debug probing to discover on first submission:
```python
def load_data(self):
    import glob as _g
    print("[DEBUG] CWD:", os.getcwd())
    print("[DEBUG] ../ files:", os.listdir(".."))
    candidates = ["./data/...", "../mnist_data", "../data/..."]
    for d in candidates:
        if os.path.exists(os.path.join(d, "train-images-idx3-ubyte")):
            found = d; break
    if not found:
        found = os.path.dirname(_g.glob("**/train-images*", recursive=True)[0])
    # use 'found' as data dir
```

One debug submission replaces multiple guesswork submissions.

## batch_size=10000 Breaks Training

The 2.2 DLP submission requires `batch_size=10000` for inference, but training
with batch_size=10000 gives only 6 batches/epoch (60000/10000). Accuracy collapses
from 98% to 91%. Fix: train with batch_size=100, then switch:

```python
def build_mnist_mlp(param_dir='weight.npy'):
    mlp = MNIST_MLP(batch_size=100, ...)  # train batch
    mlp.train()
    mlp.batch_size = 10000                # inference batch
    mlp.load_model(param_dir)
```

## Module-Level Constants for DLP

The platform's `main_exp_2_2.py` imports from demo:
```python
from stu_upload.mnist_mlp_demo import MNIST_MLP, HIDDEN1, HIDDEN2, OUT
```

Must export these at module level in `mnist_mlp_demo.py`:
```python
HIDDEN1 = 128
HIDDEN2 = 64
OUT = 10
```

## Pycnnl loadParams Indices

ReLU layers count toward the layer index. For: FC1→ReLU→FC2→ReLU→FC3→Softmax,
FC layers are at indices 0, 2, 4 (not 0, 1, 2):
```python
net.loadParams(0, w1, b1)   # fc1
net.loadParams(2, w2, b2)   # fc2 (skip relu1 at index 1)
net.loadParams(4, w3, b3)   # fc3 (skip relu2 at index 3)
```

## NumPy Pickle Compatibility

Platform runs Python 3.7 + NumPy 1.19. Weights trained on Python 3.10 + NumPy 1.26
use pickle protocol 5, which Python 3.7 can't read. Convert with script:
`scripts/convert_npy_protocol2.py` (in agent-work-frame skill).

## Missing Packages on Grading Platform

The grading platform typically has: **NumPy**, **SciPy**, **Pillow** installed. Packages listed only for convenience (e.g., `imageio`, `cv2`) are usually **NOT** available.

Common pitfalls:

| Package | Status | Fix |
|---------|--------|-----|
| `imageio` | ❌ Not installed | Use `PIL.Image.open(path).convert('RGB')` |
| `cv2` / `opencv-python` | ❌ Not installed | Comment out imports if unused; otherwise use PIL |
| `scipy.misc` | ⚠️ Deprecated | Use `PIL.Image` instead |
| `PIL` / `Pillow` | ✅ Installed | Safe to use |
| `numpy` | ✅ Installed | Safe |
| `scipy.io` | ✅ Installed | Safe for `.mat` loading |

**Pattern for platform-safe image loading** (requires only Pillow):
```python
from PIL import Image
import numpy as np

pil_img = Image.open(image_path).convert('RGB')
pil_img = pil_img.resize((224, 224), Image.BILINEAR)  # NOT Image.Resampling.LANCZOS
img_array = np.array(pil_img, dtype=np.float32)
```

No `imageio`, no `scipy.misc`, no `cv2` needed.
  
**Pillow version trap**: The grading platform runs Pillow **7.2.0**, which uses the old-style enum directly (`Image.LANCZOS`, `Image.BILINEAR`, etc.). Pillow 9+ introduced the `Image.Resampling` namespace. Using `Image.Resampling.LANCZOS` on Pillow 7.x raises:  
`AttributeError: module 'PIL.Image' has no attribute 'Resampling'`  
Always use the bare constant (e.g., `Image.BILINEAR`) for cross-version compatibility and to match the platform's `scipy.misc.imresize` interpolation behavior.

## Probe-Then-Fix Pattern

1. Add debug prints to entry points (print CWD, list dirs, try multiple paths)
2. Submit once → read error + [DEBUG] output
3. Fix the single blocking issue → resubmit
4. Repeat until clean pass

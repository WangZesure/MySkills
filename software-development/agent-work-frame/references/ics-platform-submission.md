# ICS Platform Submission Pitfalls

Lessons from Lab2 (neural network MNIST classification on Cambricon DLP platform).

## Environment Mismatch Trap
- **Local/dev server**: Python 3.10 + NumPy 1.26
- **Platform (希冀)**: Python 3.7 + NumPy 1.19.5
- **Critical**: NumPy 1.26 uses pickle protocol 5 to save `.npy` with `allow_pickle=True`; Python 3.7 can't read it. Result: `_pickle.UnpicklingError: pickle data was truncated`.

### Fix: Save weights with pickle protocol 2
```python
import numpy as np, pickle, struct
p = {"w1": w1, "b1": b1, ...}
buf = pickle.dumps(p, protocol=2)
header = b"{'descr': '|O', 'fortran_order': False, 'shape': (), }"
pad = (16 - (10 + len(header)) % 16) % 16
header += b" " * pad + b"\n"
with open("weight.npy", "wb") as f:
    f.write(b"\x93NUMPY\x01\x00")
    f.write(struct.pack("<H", len(header)))
    f.write(header)
    f.write(buf)
```

## Import Path
- Platform extracts zip into `stu_upload/` directory
- All imports must use `from stu_upload.xxx import ...`
- Files at zip root → become `stu_upload/file.py`
- Submission zip: `__init__.py`, `layers_1.py`, `mnist_mlp_cpu.py` at root

## Data Path
- Platform MNIST at `../mnist_data/` (one level above experiment dir)
- Original tutorial uses `../data/mnist_mlp_data/mnist_data` — doesn't work on platform
- Best: add debug path search in `load_data()` that tries multiple locations

## DLP / pycnnl Specifics
- pycnnl is in Docker image `mlu370_ubuntu22.04-for-student:v6.1`
- CNNL libs at `/usr/local/neuware/lib64` (not `env/neuware`)
- NumPy must be `<2` for pycnnl `.so` compatibility
- `loadParams` indices: ReLU layers occupy slots! For FC→ReLU→FC→ReLU→FC: use 0, 2, 4
- `batch_size=10000` for **inference only** — training with batch_size=10000 gives 6 batches/epoch → 91% accuracy

## v6.1 LLM Image Specifics

In the LLM-version v6.1 image, the code layout differs from the v2/v3 images:

| Old path (v2/v3) | New path (v6.1 LLM) |
|---|---|
| `/opt/code_chap_2_3/code_chap_2_3_student/` | `/opt/code_chap6/` |
| `exp_2_1_mnist_mlp/` | `exp_6_1_NNclassification/` |
| `exp_3_1_vgg/` | `exp_6_2_VGG19classification/exp_6_2_1_infercpu/` |
| `exp_3_2_vgg_dlp/` | `exp_6_2_VGG19classification/exp_6_2_2_inferdlp/` |

**Python**: Use `/opt/py3.10/bin/python3.10` — the system `python3` has no NumPy. Install deps:
```bash
/opt/py3.10/bin/pip install numpy scipy pillow imageio
```
NumPy 2.x is fine for CPU-only experiments (no pycnnl involved). Only downgrade to 1.x for DLP.

**VGG19 weight file**: `imagenet-vgg-verydeep-19.mat` (576MB) at `../imagenet-vgg-verydeep-19.mat` relative to experiment dir.

**Template quirk**: The `vgg_cpu.py` student template has `import cv2` but never uses it. This breaks on a fresh install. Comment it out or `pip install opencv-python`.

## Training Stability
- `N(0, 0.01)` init works reliably with unnormalized 0-255 inputs
- Xavier init + unnormalized inputs → loss stuck at ln(10)
- Input normalization (/255) requires proportionally larger learning rate
- 98%+ config: hidden=128→64, 25 epochs, lr=0.01 with ×0.5 every max_epoch//3

## 2.2-specific Requirements
- `mnist_mlp_demo.py` must export: `HIDDEN1`, `HIDDEN2`, `OUT` as module-level constants
- `build_mnist_mlp()` in `mnist_mlp_cpu.py` for 2.2: skip training, use `load_model(param_dir)`, batch_size=10000

## Chapter 3 — VGG19 Image Classification

### 3.1 CPU Submission
- **Files**: `__init__.py`, `layers_1.py`, `layers_2.py`, `vgg_cpu.py` → zip
- **Grading**:
  - 60分: Conv + Pool forward correct for small matrix test
  - 80分: Full VGG19 pool5 output correct
  - 100分: Softmax output correct → class 281 (tabby cat) for cat1.jpg
- **Code path**: `exp_6_2_1_infercpu/stu_upload/`
- **Python**: `/opt/py3.10/bin/python3.10` (pre-install: pip install numpy scipy pillow imageio)
- **Weight file**: `../imagenet-vgg-verydeep-19.mat` (576MB, already on server)
- **Test command**: `python main_infer_cpu.py`

### 3.2 DLP Submission
- **Files**: `__init__.py`, `vgg19_demo.py` → zip
- **Python**: `/torch/venv3/pytorch/bin/python` (pycnnl in this venv)
- **LD_LIBRARY_PATH**: `/usr/local/neuware/lib64` (for libcnnl.so.1)
- **No Flatten layer** needed in DLP net (pycnnl handles it)
- **Image input is NHWC** (not NCHW as in CPU version)
- **Test command**: `LD_LIBRARY_PATH=/usr/local/neuware/lib64 /torch/venv3/pytorch/bin/python main_infer_dlp.py`

### .mat File Weight Index Mapping

The `.mat` file has 43 layers. `params['layers'][0][mat_idx]` maps to:

| mat_idx | Layer | Has Weights? |
|---------|-------|-------------|
| 0 | conv1_1 | ✅ weight+bias |
| 1 | relu1_1 | ❌ |
| 2 | conv1_2 | ✅ |
| ... | (alternates conv/relu/pool) | ... |
| 34 | conv5_4 | ✅ |
| 35-36 | relu5_4 + pool5 | ❌ |
| **37** | **flatten** | **✅ fc6 weights here!** |
| 38 | fc6 name cell | ❌ |
| **39** | **(relu6)** | **✅ fc7 weights here!** |
| 40 | fc7 name cell | ❌ |
| **41** | **(relu7)** | **✅ fc8 weights here!** |
| 42 | fc8 name cell | ❌ |

**Critical**: FC weight entries are at 37, 39, 41 (not 38, 40, 42). The fc name cells at 38, 40, 42 contain type/name metadata only.

Conv param_layer_name indices for iteration (CPU): see `vgg_cpu.py` param_layer_name tuple — conv at idx `[0,2,5,7,10,12,14,16,19,21,23,25,28,30,32,34]`

### Template Quirks (v6.1 mirror)
- `vgg_cpu.py` imports `cv2` but never uses it — comment out to avoid `ModuleNotFoundError`
- `layers_1.py` has TODO blanks for fc/relu/softmax forward — must fill them even for inference-only
- VGG19 with 4-loop conv takes ~337s on CPU for full forward pass

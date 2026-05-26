# ICS / Cambricon DLP Platform Quirks (lab2)

Lessons from submitting ICS (智能计算系统) lab2 experiments to the course auto-grading platform.

## Platform Structure

The platform extracts the submitted zip into `stu_upload/` inside the experiment directory:

```
/cg/exp_2_1_mnist_mlp/          # experiment 2.1
  stu_upload/                    # your zip extracted here
    __init__.py
    layers_1.py
    mnist_mlp_cpu.py
  main_exp_2_1.py                # platform's test harness

/cg/exp_2_2_mnist_mlp_dlp/      # experiment 2.2
  stu_upload/
    mnist_mlp_demo.py
  main_exp_2_2.py
  test_cpu.py

/cg/mnist_data/                  # MNIST data (outside experiment dirs)
  train-images-idx3-ubyte
  ...
```

**Key implications:**
- Imports must be `from stu_upload.layers_1 import ...` (NOT `from layers_1 import ...`)
- MNIST data is at `../mnist_data/` relative to experiment dir CWD
- The platform's `main_exp_2_1.py` imports from `stu_upload.mnist_mlp_cpu`

## 2.2 Submission Requirements

Additional files beyond 2.1:
- `mnist_mlp_demo.py` — must export `HIDDEN1`, `HIDDEN2`, `OUT` as module-level ints
- `weight.npy` — pre-trained model (rename from `mlp-H1-H2-Nepoch.npy`)

`mnist_mlp_cpu.py` for 2.2 must be modified:
- `build_mnist_mlp()`: use `batch_size=100` for training, then `mlp.batch_size = 10000` for inference
- Comment out `mlp.train()` and `mlp.save_model()` — load pre-trained weight only
- `mlp.load_model(param_dir)` where `param_dir` comes from the function parameter

`mnist_mlp_demo.py` platform requirements:
- Module-level: `HIDDEN1 = 128`, `HIDDEN2 = 64`, `OUT = 10`
- Data paths: `../mnist_data/t10k-images-idx3-ubyte` and `../mnist_data/t10k-labels-idx1-ubyte`
- Model path: `weight.npy` (the platform passes this)
- `loadParams` indices: 0 (fc1), 2 (fc2), 4 (fc3) — ReLU layers also occupy indices
- Weights must be `np.float64` (cast from float32)

## pycnnl Setup (Server-Side)

The pycnnl Python library is pre-compiled on platform images (`mlu370_ubuntu22.04-for-student:v6.1`):

**Location**: PyTorch venv at `/torch/venv3/pytorch/lib/python3.10/site-packages/pycnnl.py`

```bash
# Use the PyTorch venv Python (has pycnnl pre-installed)
export LD_LIBRARY_PATH=/usr/local/neuware/lib64:$LD_LIBRARY_PATH
/torch/venv3/pytorch/bin/python your_script.py
```

Common pitfalls:
- `libcnnl.so.1` not found → add `/usr/local/neuware/lib64` to `LD_LIBRARY_PATH`
- NumPy 2.x incompatible with pre-built pycnnl → `pip install "numpy<2"` (use 1.26.4)
- `CnnlNet()` constructor takes ~10s on first call (MLU device initialization)
- Use PyTorch venv Python; `/opt/py3.10/bin/python3.10` does NOT have pycnnl

## pycnnl API Reference (VGG19)

Layer creation methods on `pycnnl.CnnlNet()`:

| Method | Signature | Notes |
|--------|-----------|-------|
| `createConvLayer` | `(name, input_shape, out_channel, kernel_size, stride, dilation, pad)` | input_shape=IntVector(4) [N,C,H,W] |
| `createReLuLayer` | `(name)` | - |
| `createPoolingLayer` | `(name, input_shape, kernel_size, stride)` | NOT createMaxpoolLayer! |
| `createMlpLayer` | `(name, input_shape, weight_shape, output_shape)` | For FC layers |
| `createSoftmaxLayer` | `(name, input_shape, axis)` | axis=1 for class dim |
| `loadParams` | `(layer_id, filter_data, bias_data)` | Both are flat float64 arrays |
| `setInputShape` | `(N, C, H, W)` | - |
| `setInputData` | `(data)` | Flat 1D float64 array |
| `forward` | `()` | Runs inference |
| `getOutputData` | `()` | Returns result as list |
| `getLayerName` | `(idx)` | Returns layer name string |
| `size` | `()` | Returns number of layers |

**IntVector usage:**
```python
iv = pycnnl.IntVector(4)
iv[0] = 1; iv[1] = 3; iv[2] = 224; iv[3] = 224  # NCHW order
```

### VGG19 DLP Weight Loading

#### Conv layers: .mat → DLP format
```python
# MatConvNet: [height, width, in_channel, out_channel]
# DLP expects: [out_channel, height, width, in_channel] → flattened
weight = np.transpose(weight, [3, 0, 1, 2]).flatten().astype(np.float64)
```

.mat param_layer_name conv indices: `[0, 2, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34]`

#### FC layers: .mat → DLP format  
```python
# MatConvNet stores fc weights at the "flatten" entry in the .mat file
# fc6 at mat[37], fc7 at mat[39], fc8 at mat[41]
# Just flatten (no reshape/transpose)
weight = weight.flatten().astype(np.float64)
```

**Key difference from CPU**: DLP weight loading uses `.mat` file param_layer_name indices (not DLP net layer indices). Map via fixed index arrays.

.mat fc_param_idx: `[37, 39, 41]` (not 38, 40, 42 — entries at 38, 40, 42 are fc's metadata cells)

### Image Input Format

**DLP expects NHWC** — do NOT transpose to NCHW:
```python
input_image = np.reshape(input_image, [1] + list(input_image.shape))  # [1, 224, 224, 3]
input_data = input_image.flatten().astype(np.float64)
self.net.setInputData(input_data)
```

No flatten layer needed (DLP handles it internally).

### Complete VGG19 DLP Build Pattern

```python
self.net.setInputShape(1, 3, 224, 224)

# Stage 1
self.net.createConvLayer('conv1_1', input_shape, 64, 3, 1, 1, 1)
self.net.createReLuLayer('relu1_1')
self.net.createConvLayer('conv1_2', input_shape, 64, 3, 1, 1, 1)
self.net.createReLuLayer('relu1_2')
self.net.createPoolingLayer('pool1', input_shape, 2, 2)

# ... more stages with shrinking spatial dims (224→112→56→28→14→7)
# Each stage: NxConv → NxReLU → 1xPool

# FC layers (no Flatten!)
self.net.createMlpLayer('fc6', input_25088, weight_25088_4096, output_4096)
self.net.createReLuLayer('relu6')
self.net.createMlpLayer('fc7', input_4096, weight_4096_4096, output_4096)
self.net.createReLuLayer('relu7')
self.net.createMlpLayer('fc8', input_4096, weight_4096_1000, output_1000)
self.net.createSoftmaxLayer('softmax', input_1000, 1)
```

## Debug Probe Pattern for Unknown Platform Paths

When the platform's data or file structure is unknown, add a self-discovering `load_data()`:

```python
def load_data(self):
    import glob as _g, os
    print("[DEBUG] CWD:", os.getcwd())
    print("[DEBUG] CWD files:", os.listdir("."))
    print("[DEBUG] ../ files:", os.listdir(".."))
    candidates = [
        "./data/mnist_mlp_data/mnist_data",
        "../data/mnist_mlp_data/mnist_data",
        "../mnist_data",
    ]
    mnist_dir = None
    for d in candidates:
        if os.path.exists(os.path.join(d, "train-images-idx3-ubyte")):
            mnist_dir = d
    if mnist_dir is None:
        found = _g.glob("**/train-images-idx3-ubyte", recursive=True)
        found += _g.glob("../**/train-images-idx3-ubyte", recursive=True)
        if found:
            mnist_dir = os.path.dirname(found[0])
    if mnist_dir is None:
        raise FileNotFoundError("MNIST data not found!")
    print("[DEBUG] Using MNIST dir:", mnist_dir)
```

This pattern prints the platform's actual directory structure, enabling a one-shot fix.

## NumPy Pickle Cross-Version Incompatibility

When submitting pre-trained `.npy` weights: NumPy 1.26 (Python 3.10) uses pickle protocol 5 by default for dict-saved arrays. Auto-grading platforms using NumPy 1.19.5 (Python 3.7) can't read them.

**Fix**: Re-save with pickle protocol 2:

```python
import numpy as np, pickle, struct, io

p = np.load("weight.npy", allow_pickle=True).item()
buf = io.BytesIO()
pickle.dump(p, buf, protocol=2)
data = buf.getvalue()

header = "{'descr': '|O', 'fortran_order': False, 'shape': (), }"
header_bytes = header.encode('ascii')
pad = (16 - (10 + len(header_bytes)) % 16) % 16
header_bytes += b' ' * pad + b'\n'

with open("weight.npy", "wb") as f:
    f.write(b'\x93NUMPY')
    f.write(b'\x01\x00')
    f.write(struct.pack('<H', len(header_bytes)))
    f.write(header_bytes)
    f.write(data)
```

**Alternative**: Let the platform train instead of loading pre-trained weights. For 2.2, uncomment `train()` and `save_model()` in `build_mnist_mlp()`. The platform's own NumPy will produce a compatible file.

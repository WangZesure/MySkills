# ICS Lab3 V6.1 Platform Quirks (VGG19 Image Classification)

Lessons from running ICS Chapter 3 (VGG19 image classification) on the LLM-version platform image `mlu370_ubuntu22.04-for-student:v6.1`.

## Path Structure (v6.1 — different from v3.0)

The v6.1 LLM image reorganizes the code tree:

```
/opt/code_chap6/                          # Chapter 6 absorbs Ch2-5 in LLM version
  README.txt                              # Explains the mapping
  exp_6_1_NNclassification/               # = old Ch2 (3-layer MLP)
  exp_6_2_VGG19classification/            # = old Ch3 (VGG19)
    cat1.jpg                              # Test image
    imagenet-vgg-verydeep-19.mat          # Pretrained weights (576MB)
    readme.txt                            # Lists exp_3_1, exp_3_2, exp_3_3 dirs
    exp_6_2_1_infercpu/                   # = old exp_3_1_vgg (CPU version)
      main_infer_cpu.py                   # Test harness (imports from stu_upload)
      stu_upload/
        layers_1.py                       # FullyConnected, ReLU, Softmax (TODO)
        layers_2.py                       # Conv, MaxPool, Flatten (TODO)
        vgg_cpu.py                        # VGG19 class (TODO)
    exp_6_2_2_inferdlp/                   # = old exp_3_2_vgg_dlp (DLP version)
```

**Key difference**: Old docs say `/opt/code_chap_2_3/code_chap_2_3_student/exp_3_1_vgg/`. On v6.1 it's `/opt/code_chap6/exp_6_2_VGG19classification/exp_6_2_1_infercpu/`.

## NumPy / SciPy / Pillow — NOT Pre-Installed

v6.1 image does NOT pre-install NumPy. Must install:

```bash
/opt/py3.10/bin/pip install numpy scipy pillow imageio
```

The system `python3` and even `/opt/py3.10/bin/python3.10` lack numpy until pip install.

**Python to use**: `/opt/py3.10/bin/python3.10` (there's also `/usr/bin/python3.10` but no numpy there).

## cv2 Import — Dead Code

`vgg_cpu.py` template has `import cv2` at the top but never uses it. OpenCV is not installed. Comment it out:

```python
# import cv2
```

Actual image loading uses `PIL.Image.open().convert('RGB')` + resize (no imageio dependency needed).

## imageio on Grading Platform

⚠️ **The grading platform does NOT have `imageio` installed.** If your submission uses `import imageio.v2 as imageio`, it will get `ModuleNotFoundError` and score 0.

**Fix**: Replace imageio with PIL-only loading:
```python
from PIL import Image
pil_img = Image.open(image_dir).convert('RGB')
pil_img = pil_img.resize((224, 224), Image.Resampling.LANCZOS)
self.input_image = np.array(pil_img, dtype=np.float32)
```

This is safe because Pillow is a required dependency for the experiment.

## VGG19 4-Loop CPU Inference Time

Pure 4-loop NumPy convolution on CPU (~2.2GHz):

| Layer | Input Shape | Time (approx) |
|-------|------------|---------------|
| conv1_1 | [1,3,224,224] → [1,64,224,224] | ~15s |
| conv5_× | [1,512,14,14] → [1,512,14,14] | ~20s each |
| Total 43 layers | — | **~337s (5.6 min)** |

3 parallel processes on the same server will cause memory pressure (>800MB each) and may OOM.

## main_infer_cpu.py Structure

The test harness already implements `forward(vgg)` and `evaluate(vgg)` externally:

```python
# main_infer_cpu.py already does:
from stu_upload.vgg_cpu import VGG19
vgg = VGG19(param_path='../imagenet-vgg-verydeep-19.mat')
vgg.build_model()
vgg.init_model()
vgg.load_model()
vgg.load_image('../cat1.jpg')
pool5 = evaluate(vgg)  # calls forward() internally
```

`vgg_cpu.py` only needs `build_model()`, `load_model()`, `load_image()`, `forward()`, `evaluate()`. The `main_infer_cpu.py` duplicates some logic (it has its own `forward()` and `evaluate()`) but still calls `vgg_cpu`'s methods through `VGG19.evaluate()` if the TODOs are filled.

## Weight File (.mat) Path

Weights are at `../imagenet-vgg-verydeep-19.mat` relative to the experiment directory (one level up from `exp_6_2_1_infercpu/` to `exp_6_2_VGG19classification/`).

## MatConvNet Weight Format

```
MatConvNet: [height, width, in_channel, out_channel]
Our format: [in_channel, height, width, out_channel]
```

Transpose: `np.transpose(weight, [2, 0, 1, 3])`

## Pool5 Check (80-point gate)

`main_infer_cpu.py` has a `check_pool5()` function that compares against `pool5_dump.npy` (if present). Commented out by default. MSE threshold: < 0.003.

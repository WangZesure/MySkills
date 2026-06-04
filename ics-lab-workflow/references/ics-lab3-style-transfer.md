# ICS Lab3 Style Transfer (3.3) — Implementation Reference

## Overview

Non-real-time style transfer using VGG19 feature extraction + Content/Style loss + iterative optimization. CPU-only, ~20 lines of student code.

## File Structure

```
exp_3_3_style_transfer/
  __init__.py
  layers_1.py           ← FC/ReLU/Softmax (reused from 3.1)
  layers_2.py           ← Conv+Pool+Flatten (with backward added)
  layers_3.py           ← NEW: ContentLossLayer + StyleLossLayer
  exp_3_3_style_transfer.py  ← VGG19(conv-only) + training loop
  output.jpg            ← Generated transfer result
```

## Backward Implementations (60分 level)

### ConvolutionalLayer.backward()

Standard 4-loop backward. Forward stores `self.input_pad` and `self.input`; backward computes:

```python
# d_weight: sum over N,H,W of (input_pad_window × top_diff)
self.d_weight[:,:,:,c] += input_pad[n,:,h:h+K,w:w+K] * top_diff[n,c,h,w]

# d_bias: sum over N,H,W of top_diff
d_bias = np.sum(top_diff, axis=(0, 2, 3))

# d_input: full convolution of top_diff with rotated (180°) weight
rot_weight = self.weight.transpose(3,1,2,0)[:,::-1,::-1,:]
top_diff_pad = np.pad(top_diff, ((0,0),(0,0),(K-1,K-1),(K-1,K-1)))
bottom_diff[n,cin,h,w] = sum(top_diff_pad[n,:,h:h+K,w:w+K] * rot_weight[:,:,:,cin])
```

### MaxPoolingLayer.backward()

Record max positions in forward, pass gradient only to max positions:

```python
# Forward: record max_idx_h/w
self.max_idx_h[n,c,h,w] = argmax_row
self.max_idx_w[n,c,h,w] = argmax_col

# Backward: gradient only at max position
bottom_diff[n,c, h*S+max_h, w*S+max_w] = top_diff[n,c,h,w]
```

## Content Loss (80分 level)

Layer: `relu4_2` (conv4_2's ReLU output)

Formula (3.10):
```
L_content = 0.5 * Σ(F - P)² / (N*C*H*W)
```

Gradient (3.11):
```
dL/dF = (F - P) / (N*C*H*W)
```

Implementation:
```python
class ContentLossLayer:
    def forward(self, output, target):
        N,C,H,W = output.shape
        diff = output - target
        self.loss = 0.5 * np.sum(diff**2) / (N*C*H*W)
        return self.loss

    def backward(self, output, target):
        return (output - target) / (output.shape[0] * output.shape[1] * output.shape[2] * output.shape[3])
```

## Style Loss (80分 level)

Layers: `relu1_1`, `relu2_1`, `relu3_1`, `relu4_1`, `relu5_1`

Gram Matrix (3.12):
```
G[i][j] = Σ_k F[i][k] * F[j][k] / (C*H*W)   # F is [C, H*W]
```

Style Loss (3.13):
```
E_l = Σ_ij (G_ij - A_ij)² / (4*C²*(H*W)²)
```

Gradient (3.15):
```
dE/dF = (G - A)^T @ F / (C²*(H*W)²)
```

Implementation:
```python
class StyleLossLayer:
    def _gram_matrix(self, x):
        N,C,H,W = x.shape
        F = x.reshape(C, H*W)
        return np.matmul(F, F.T) / (C * H * W)

    def backward(self, output, target):
        N,C,H,W = output.shape
        F = output.reshape(C, H*W)
        G = self._gram_matrix(output)
        A = self._gram_matrix(target)
        dF = np.matmul(G - A, F) / (C * C * H * W * H * W)
        return dF.reshape(N, C, H, W)
```

## Training Loop (80分 level)

```python
CONTENT_LOSS_LAYERS = ['relu4_2']
STYLE_LOSS_LAYERS  = ['relu1_1','relu2_1','relu3_1','relu4_1','relu5_1']
ALPHA, BETA = 1, 500
TRAIN_STEP = 2001
LEARNING_RATE = 1.0
IMAGE_HEIGHT, IMAGE_WIDTH = 192, 320

# Init
vgg = VGG19(param_path='../imagenet-vgg-verydeep-19.mat')
vgg.build_model(); vgg.init_model(); vgg.load_model()

# Extract target features
content_layers = vgg.forward(content_image, CONTENT_LOSS_LAYERS)
style_layers   = vgg.forward(style_image,   STYLE_LOSS_LAYERS)

# Iterate
for step in range(TRAIN_STEP):
    t_layers = vgg.forward(transfer_image, CONTENT_LOSS_LAYERS + STYLE_LOSS_LAYERS)

    # Content
    for layer in CONTENT_LOSS_LAYERS:
        content_loss_layer.forward(t_layers[layer], content_layers[layer])
        content_diff += vgg.backward(
            content_loss_layer.backward(t_layers[layer], content_layers[layer]),
            layer)

    # Style
    for layer in STYLE_LOSS_LAYERS:
        style_loss_layer.forward(t_layers[layer], style_layers[layer])
        style_diff += vgg.backward(
            style_loss_layer.backward(t_layers[layer], style_layers[layer]),
            layer)

    total_grad = ALPHA * content_diff + BETA * style_diff
    transfer_image -= LEARNING_RATE * total_grad  # or use Adam
```

## Performance (4-loop CPU, 192×320)

| Component | Time | Notes |
|-----------|------|-------|
| VGG19 Forward | ~31s @64×64 | Scales with H*W, 192×320 ≈ 5× larger |
| VGG19 Backward | ~63s @64×64 | ~2× forward |
| Per iteration | ~94s @64×64 | ~470s @192×320 |
| 1001 iterations | ~26h @192×320 | Impractical with 4-loop |

**100分 optimization**: Replace 4-loop convolution with im2col (matrix multiply). Expected speedup: 10-50×. Each conv becomes a single `np.dot()` call instead of 4 nested loops.

## Adam Optimizer

```python
class AdamOptimizer:
    def __init__(self, lr, shape, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr = lr
        self.beta1, self.beta2, self.eps = beta1, beta2, eps
        self.m = np.zeros(shape)
        self.v = np.zeros(shape)
        self.t = 0

    def update(self, params, grads):
        self.t += 1
        self.m = self.beta1 * self.m + (1 - self.beta1) * grads
        self.v = self.beta2 * self.v + (1 - self.beta2) * (grads**2)
        m_hat = self.m / (1 - self.beta1**self.t)
        v_hat = self.v / (1 - self.beta2**self.t)
        return params - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
```

# im2col Convolution Optimization (CPU)

Replace the 4-loop CPU convolution with im2col + GEMM for 50-500x speedup. Used in ICS lab3 style transfer (100分 requirement).

## Why im2col

The naive 4-loop convolution touches scattered memory per iteration and is very slow for large C_in/C_out.

im2col unfolds input patches into a matrix, then uses BLAS-level matrix multiply.

## Algorithm

**Forward**: X -> pad -> im2col -> col @ W_mat.T -> reshape -> Y  
**Backward**: dY -> dW = dout.T @ col; dcol = dout @ W_mat -> col2im -> dX  
**d_bias**: sum(dY, axis=(0,2,3))

## Speedups (Measured on ICS lab3 VGG19, CPU)

| Layer | Input | 4-loop fwd | im2col fwd | Speedup |
|-------|-------|-----------|------------|---------|
| conv1_1 | 3->64@64x64 | 2.84s | 0.005s | 534x |
| conv2_1 | 64->128@32x32 | 2.03s | 0.009s | 220x |
| conv4_1 | 512->512@14x14 | 7.85s | 0.103s | 76x |
| Full VGG19 | 192x320 image | ~377s/step | ~11s/step | ~34x |

## Pitfalls

- Memory: im2col expands input by K^2 (9x for 3x3 kernel)
- Not for DLP/pycnnl - use native layers
- Weight stored as [C_out, C_in*K*K]; use load_param() to convert from [C_in,K,K,C_out]
- Small inputs (HxW < 16): 4-loop may be competitive

## Usage Pattern for ICS Style Transfer 100分

1. Build VGG19 with ConvolutionalLayerOpt instead of ConvolutionalLayer
2. load_param() converts weight format automatically
3. Keep MaxPoolingLayer unchanged (pooling is already fast)
4. Report speedup ratio vs 4-loop for 100分 requirement

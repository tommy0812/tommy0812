## Tommy Chen (陳龍懷)

**Senior AI Algorithm Engineer — Model Compression & Edge Deployment**
Compal Electronics · M.S. Electrical and Computer Engineering, NYCU

I build vision models small enough and fast enough to run on embedded hardware, and I
measure every step of the way: structured pruning → knowledge distillation → post-training
quantization with block-wise reconstruction → ONNX Explicit QDQ → TensorRT INT8 →
NVIDIA Jetson AGX Orin. Earlier I worked the other end of the same problem — recovering
metric scale for monocular depth on embedded hardware.

---

### 📊 [MobileViTv3 — Vision Transformer Compression Study](https://github.com/tommy0812/model-compression/blob/main/MobileViTv3_Compression.md)

A measured compression pipeline on ImageNet-100, from pruning through to INT8 TensorRT engines on
three platforms — every number from a `trtexec` log or a full validation run:

| | |
|---|---|
| **Pruning** | MobileViTv3-XS down to the XXS MAC budget: **−54% parameters**, **+1.22 pp Top-1** over the XXS-KD baseline |
| **PTQ reconstruction** | **+4.5–4.7 pp Top-1 over NVIDIA ModelOpt** at 4–8% lower latency, on all three platforms |
| **Deployment** | INT8 TensorRT on RTX 4090, RTX 4050 and Jetson AGX Orin — with residual-add quantization **1.7–2.3× FP32 speed** and faster than FP16 on every platform, within 0.34 pp of FP32 Top-1 |
| **INT8 coverage** | **95% of layers (77/81)** with residual-add quantization, against 53% for TensorRT's implicit PTQ |

---

### 🎯 [Metric-Scale Monocular Depth Estimation — M.S. Thesis](https://github.com/tommy0812/tommy0812/blob/main/Depth_Estimation_Thesis.md)

Recovering real-world scale for self-supervised monocular depth using instance-segmented
objects as a stereo texture prior, evaluated against LiDAR ground truth and in RGB-D SLAM:

| | |
|---|---|
| **Scale-recovery runtime** | **17 ms** vs. 418 ms for the dense-geometry baseline — **24.6× faster** (Jetson AGX Xavier) |
| **Depth accuracy** | Lowest RMSE on all 4 datasets; best Abs Rel and δ<1.05 in the 0–10 m band |
| **SLAM trajectory** | Lowest mean ATE on **all 11 sequences** — −25.2% vs. RGB-LD |
| **Relocalization** | **98.3%** and **99.8%** against maps built 5 months earlier |

---

### What I work on

- **Model compression** — structured pruning for CNNs (Group Fisher Pruning) and Vision
  Transformers (P3B block pruning), knowledge distillation, PTQ/QAT
- **Quantization** — block-wise PTQ reconstruction (QDrop, APHQ-ViT, LS-ViT), in-house INT8
  fake-quantization framework with per-channel weights, BN folding, and automated calibration
- **Edge deployment** — PyTorch → ONNX Explicit QDQ → TensorRT 10.x, benchmarked on
  Jetson AGX Orin / AGX Xavier
- **Perception** — object detection, super-resolution-assisted small-object detection,
  monocular depth estimation, LiDAR / Radar / Camera sensor fusion on ROS

### Contact

[LinkedIn](https://linkedin.com/in/tommychen19920812) · a0912986300@gmail.com

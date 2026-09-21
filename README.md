## Tommy Chen (陳龍懷)

**Senior AI Algorithm Engineer — Model Compression & Edge Deployment**
Compal Electronics · M.S. Electrical and Computer Engineering, NYCU

I build vision models small enough and fast enough to run on embedded hardware, and I
measure every step of the way: structured pruning → knowledge distillation → post-training
quantization with block-wise reconstruction → ONNX Explicit QDQ → TensorRT INT8 →
NVIDIA Jetson AGX Orin. Most of that work now points at depth — compressing depth estimation
models, and earlier, recovering metric scale for monocular depth on embedded hardware.

---

### 🧭 [Depth Anything 3 — Compressing a Depth Estimation Model](https://github.com/tommy0812/model-compression/blob/main/DA3_Compression_Results.md)

Taking the compression pipeline below from classification to multi-view metric depth, where the
output is geometry and every difference carries a confidence interval *(in progress)*:

| | |
|---|---|
| **Compute parity** | 729.1 → **205–210 GFLOPs** vs. DA3-Small's 205.6 (101.97M → 26–32M params) |
| **Free compute found by profiling** | **31.5 GFLOPs removed bit-exactly** — the DualDPT head runs three auxiliary branches whose output is never read |
| **Distillation after pruning** | worth **4×** more than on the released small model (−0.0045 vs. −0.0011 abs_rel) |
| **Headline result** | **negative, and reported as such** — a pruned DA3-BASE does not reach a DA3-Small carrying full DINOv2 pretraining |

---

### 📊 [Model Compression & Edge Deployment — Full Results](https://github.com/tommy0812/model-compression)

A complete, benchmarked compression pipeline on MobileViTv3 / ImageNet-100 — per-method
tables, RTX 4090 vs. Jetson Orin engine comparison, the papers re-implemented, and how INT8
coverage was actually measured:

| | |
|---|---|
| **Pruning** | 1.91M → 0.61M params (**−68%**), 56.4M → 17.6M MACs (**−69%**) |
| **Accuracy recovery** | **62.74%** Top-1 — **+5.96 pp** over the XXS-KD baseline |
| **Quantization** | **62.30%** Top-1 INT8 — +0.56 pp vs. AdaRound, +0.26 pp vs. APHQ-ViT |
| **Jetson AGX Orin** | **62.40%** Top-1 (−0.34 pp vs. FP32), **0.864 ms** / **1,118 QPS** |
| **INT8 coverage** | **96.6%** of compute-bound layers (57/59) vs. 66.7% for NVIDIA ModelOpt |

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
- **Quantization** — Hessian-aware block-wise PTQ reconstruction (LS-ViT, APHQ-ViT,
  AdaRound), in-house INT8 fake-quantization framework with per-channel weights, BN folding,
  and automated calibration
- **Edge deployment** — PyTorch → ONNX Explicit QDQ → TensorRT 10.x, benchmarked on
  Jetson AGX Orin / AGX Xavier
- **Perception** — object detection, super-resolution-assisted small-object detection,
  monocular depth estimation, LiDAR / Radar / Camera sensor fusion on ROS

### Contact

[LinkedIn](https://linkedin.com/in/tommychen19920812) · a0912986300@gmail.com

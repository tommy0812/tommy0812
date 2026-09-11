# RGB-SD — Metric-Scale Monocular Depth by Object Stereo Scale Recovery

**M.S. thesis · National Yang Ming Chiao Tung University · January 2023**

*By [Tommy Chen (陳龍懷)](https://linkedin.com/in/tommychen19920812)*

Self-supervised monocular depth networks train without depth ground truth, which makes them
cheap to scale and scale-ambiguous by construction: the shape of the scene is right, the units
are arbitrary. Anything that needs real distances — SLAM, collision warning, an AR head-up
display placing a graphic at a specific range — cannot use that output directly.

**RGB-SD** recovers the missing scale per frame, from the camera itself, in **17 ms** on a
Jetson AGX Xavier — **24.6× faster than the dense-geometry method it replaces**, at equal
depth accuracy and with lower trajectory error on every sequence tested.

---

## TL;DR

| | |
|---|---|
| **Task** | Metric depth from a monocular camera, self-supervised (no depth ground truth) |
| **Idea** | Use *instance-segmented objects* to sample short-range stereo depth, and take the median ratio against relative depth as the per-frame scale |
| **Scale-recovery runtime** | **17 ms** vs. **418 ms** for DGC on Jetson AGX Xavier — **24.6× faster** |
| **Depth accuracy** | Lowest RMSE of all three methods on **all 4** evaluation datasets (LiDAR ground truth, 0–30 m) |
| **SLAM trajectory** | Lowest mean ATE on **all 11** sequences — **−25.2%** vs. RGB-LD, **−13.7%** vs. RGB-DGCD |
| **Relocalization** | **98.3%** (6,232/6,341) and **99.8%** (7,080/7,092) against maps built **5 months earlier** |
| **Deployed sensor set** | Camera only — LiDAR is used for evaluation and calibration, never at inference |

---

## The problem

Each existing option fails in a way that matters for a shipped product:

| Approach | Why it fails |
|---|---|
| **Stereo camera** | Holes and wrong depth in low-texture or repeating-texture regions |
| **RGB-D camera** | Sunlight interference — indoor use only |
| **Monocular depth network** | Dense and cheap, but has no real-world scale |
| **Radar scale recovery** | Projection error makes it insufficiently accurate |
| **LiDAR scale recovery (RGB-LD)** | Accurate but expensive, and a 20-frame moving average cannot track scale changes in time |
| **Dense Geometrical Constraint (DGC)** | More accurate than radar or LiDAR recovery, but **418 ms/frame** — far too slow |

So the target was a method that keeps DGC's accuracy, costs a fraction of its compute, and
adds no sensor to the deployed system.

---

## Method

```text
INPUTS
  RGB ──────────────┬──────────────────────────────────┐
                    │                                  │
  Stereo Depth ─┐   ▼                                  ▼
   (3 – 10 m)   │  YolactEdge (ResNet-50)       Monodepth2 (ResNet-50)
                │  instance segmentation         1280 × 640
                │        │                              │
                │        ▼                              ▼
                │  Binary Object Mask            Relative Depth (dense)
                │        │                              │
                └────────┴──► Stereo Object Depth       │
                              (sparse, metric)          │
                                     │                  │
  SCALE RECOVERY                     ▼                  ▼
                        Scale map = D_object / D_relative   (keep points > 0)
                                     │
                       valid scale points > 20,000 ?
                            │                     │
                          TRUE                  FALSE
                            │                     │
                            ▼                     ▼
                f_scale = median(scale map)    DGC layer:
                         [SD path]             f_scale = h_real / h_median
                            │                     │
                            └─────────┬───────────┘
                                      ▼
                        D_absolute = f_scale × D_relative
                                      ▼
                        ORB-SLAM2, RGB-D mode  (depth > 20 m zeroed)
```

### SD path — object stereo depth

Stereo matching is reliable on textured, vertical surfaces and unreliable on road pavement,
sky, and repeating structures. Rather than filter texture heuristically, RGB-SD uses
**instance segmentation as the texture prior**: a YolactEdge mask over `person`, `car`,
`motorcycle`, `bus`, `truck`, and `pillar` selects exactly the regions where stereo can be
trusted. Multiplying that binary mask by stereo depth restricted to **3–10 m** yields a
sparse but metric object depth map.

Dividing it elementwise by the network's relative depth gives a **scale map**; its **median**
is the frame's scale factor. The median absorbs the outliers that survive masking.

### DGC fallback — and why the threshold matters

When no target object is in frame the scale map is empty and the SD factor collapses to zero.
A **20,000-point threshold** on the number of valid scale samples decides which path runs.

The threshold is not just a guard against division by zero. Below it, the objects present are
typically small and distant, and a scale computed from those few points is unstable — *wrong*
rather than merely noisy. The thesis's argument for the specific value is a nice inversion:
when few objects are visible, the road ahead is usually clear, which is exactly the condition
under which DGC's ground-plane sampling is *most* reliable. The two paths are strong in
complementary situations, so the switch hands each frame to whichever is better posed.

DGC estimates the camera height implied by the relative depth at ground pixels and takes the
ratio against the true mounting height:

```
f_scale = h_real / h_median
```

### Post-processing for SLAM

Depth beyond 20 m is zeroed before entering SLAM, because accuracy degrades sharply past that
range (see the per-band results below). This has a useful side effect: the vehicle hood, which
Monodepth2 predicts incorrectly, is also zeroed, so ORB features never land on it — while
enough valid pixels remain for RGB-D tracking.

---

## Implementation

| Component | Detail |
|---|---|
| Instance segmentation | **YolactEdge**, ResNet-50 backbone |
| Segmentation training | 71,840 train / 3,698 val images — MS COCO filtered to 5 classes + self-labelled `pillar` set from parking lots |
| Segmentation accuracy | **71.23%** box mAP, **65.69%** mask mAP @ IoU 0.50 (43.86 / 39.77 @ 0.50:0.95) |
| Monocular depth | **Monodepth2**, ResNet-50, 1280 × 640, fine-tuned 8 epochs from official 640×192 weights |
| SLAM | **ORB-SLAM2**, RGB-D mode |
| Trajectory ground truth | **LeGO-LOAM** LiDAR SLAM |
| Integration | ROS nodes + ROSBAG replay — segmentation node, depth node, SLAM node as independent processes |

### Sensors

| Platform | LiDAR | Stereo |
|---|---|---|
| SUV | Velodyne HDL-64ES3 (64-beam, 120 m) | eY3D G100 (100°×67°, 6 cm baseline) |
| Golf cart | Velodyne VLP-32C (32-beam, 200 m) | eY3D G100 + STEREOLABS ZED2i (110°×70°, 12 cm baseline) |

Stereo depth was itself validated against LiDAR on a pillar target at 15 / 10 / 5.5 / 2.5 m,
which is how the 3–10 m trust window was set — at 2.5 m the untextured pillar was estimated
at 1.393 m by the G100, a 44% error that motivated the whole texture-masking approach.

---

## Results

### 1 · Scale-recovery runtime — the headline

| Method | Post-processing per frame (Jetson AGX Xavier) |
|---|---:|
| DGC | 418 ms |
| **RGB-SD** | **17 ms** |

**24.6× faster, 401 ms saved per frame.** This is the result that makes the method deployable:
DGC's accuracy at a cost that fits inside a real-time budget.

### 2 · Depth accuracy vs. LiDAR ground truth (0–30 m)

| Dataset | Method | Abs Rel ↓ | RMSE ↓ | δ<1.05 ↑ | δ<1.1 ↑ | δ<1.25 ↑ |
|---|---|---:|---:|---:|---:|---:|
| 1 | RGB-LD | 0.198 | 4.965 | 0.110 | 0.270 | 0.773 |
| 1 | DGC | 0.109 | 3.939 | 0.410 | 0.657 | 0.892 |
| 1 | **SD** | **0.109** | **3.854** | **0.421** | **0.663** | 0.890 |
| 2 | RGB-LD | 0.185 | 4.413 | 0.088 | 0.243 | 0.840 |
| 2 | DGC | **0.088** | 3.565 | **0.542** | **0.769** | 0.918 |
| 2 | **SD** | 0.095 | **3.401** | 0.444 | 0.727 | **0.919** |
| 3 | RGB-LD | 0.164 | 5.406 | 0.146 | 0.340 | 0.912 |
| 3 | DGC | **0.100** | 4.741 | **0.474** | **0.712** | 0.927 |
| 3 | **SD** | 0.102 | **4.478** | 0.407 | 0.663 | 0.927 |
| 4 | RGB-LD | 0.164 | 3.605 | 0.097 | 0.257 | 0.888 |
| 4 | DGC | **0.092** | 3.012 | **0.422** | **0.689** | **0.913** |
| 4 | **SD** | 0.099 | **2.977** | 0.343 | 0.629 | 0.911 |

**Reading this honestly:** RGB-SD has the **lowest RMSE on all four datasets**, and DGC has a
marginally better Abs Rel on three of them (0.007 or less). The two are effectively tied on
accuracy — and RGB-SD gets there 24.6× faster. RGB-LD is clearly behind both, because its
20-frame moving average cannot update scale quickly enough.

### 3 · Depth accuracy by range band

| Range | Method | Abs Rel ↓ (ds1 / ds2 / ds3 / ds4) | δ<1.05 ↑ (ds1 / ds2 / ds3 / ds4) |
|---|---|---|---|
| 0–10 m | RGB-LD | 0.113 / 0.122 / 0.096 / 0.110 | 0.223 / 0.135 / 0.149 / 0.142 |
| 0–10 m | DGC | 0.078 / 0.066 / 0.052 / 0.044 | 0.401 / 0.487 / 0.553 / 0.674 |
| 0–10 m | **SD** | **0.070 / 0.060 / 0.040 / 0.040** | **0.500 / 0.640 / 0.760 / 0.740** |
| 10–20 m | **SD** | **0.123 / 0.084 / 0.088 / 0.082** | best RMSE in 4/4 |
| 20–30 m | **SD** | **0.217 / 0.184 / 0.205 / 0.148** | best Abs Rel in 4/4 |

In the **0–10 m band RGB-SD wins Abs Rel and δ<1.05 on every dataset** — unsurprising, since
that is where the stereo anchor lives, and it is also the band that matters most for collision
warning and AR overlay placement. Accuracy degrades past 20 m for all three methods, which is
why depth is truncated there before SLAM.

### 4 · SLAM absolute trajectory error

SUV dataset, mean ATE in metres, LeGO-LOAM LiDAR SLAM as ground truth:

| Sequence | RGB-LD | RGB-DGCD | **RGB-SD** | vs. LD | vs. DGCD |
|---|---:|---:|---:|---:|---:|
| MIRC | 1.2289 | 0.7522 | **0.7361** | −40.1% | −2.1% |
| Scene 1 | 4.3083 | 4.9530 | **3.2972** | −23.5% | −33.4% |
| Scene 1 Night | 4.3037 | 4.0713 | **3.8434** | −10.7% | −5.6% |
| Scene 2 | 3.2723 | 2.2743 | **2.1445** | −34.5% | −5.7% |
| Scene 2 Night | 3.0427 | 2.9262 | **2.1970** | −27.8% | −24.9% |
| Scene 3 | 1.8032 | 1.3859 | **1.1984** | −33.5% | −13.5% |
| Scene 4 | 1.6709 | 1.5604 | **1.3969** | −16.4% | −10.5% |
| Parking outdoor | 1.4443 | 1.4136 | **1.2229** | −15.3% | −13.5% |

Golf cart dataset (no LiDAR–camera calibration, so RGB-LD is not applicable):

| Sequence | RGB-DGCD | **RGB-SD** | Improvement |
|---|---:|---:|---:|
| MIRC (ZED2i) | 1.3538 | **1.2694** | −6.2% |
| Parking indoor (ZED2i) | 1.2187 | **1.1396** | −6.5% |
| Parking indoor (G100) | 1.2453 | **1.1373** | −8.7% |

**RGB-SD has the lowest mean ATE on all 11 sequences** — two platforms, three stereo cameras,
indoor and outdoor, day and night. Mean improvement **−25.2% vs. RGB-LD** and **−13.7% vs.
RGB-DGCD**. Night sequences improve least (−10.7%, −27.8% vs. LD), the expected signature of
this design: low light weakens segmentation, fewer frames clear the threshold, more fall
through to DGC. The system degrades toward its fallback rather than failing.

### 5 · Relocalization against aged maps

| Test | Frames tracked | Success rate |
|---|---:|---:|
| MIRC, daytime | 6,232 / 6,341 | **98.3%** |
| Pond in front of MIRC, night | 7,080 / 7,092 | **99.8%** |

The map was recorded **2022-04-21** and the localization run **2022-09-29** — a five-month gap,
different time of day, one test at night. A scale that is metric but intermittent is worse
than useless to a SLAM back-end, since one bad frame corrupts the map; these numbers are the
evidence that the per-frame switch holds up outside the sequence it was tuned on.

---

## Limitations

Stated plainly, as in the thesis:

- **The method depends on finding its objects.** In environments without the six trained
  classes, most frames fall through to DGC and the runtime advantage erodes. The fix is more
  reliable textured classes — traffic signs, light poles, Cityscapes labels.
- **Effective metric range is 20 m**, bounded by monocular depth accuracy, not by the scale
  recovery itself.
- **Monodepth2 at 1280 × 640 is the throughput bottleneck.** The thesis names the remedy
  directly: accelerate with TensorRT, or change the architecture.

---

## What I did next

That last limitation is the thread I have been pulling ever since. My current work is exactly
the "accelerate it or change the architecture" half of the problem: structured pruning for
CNNs and Vision Transformers, knowledge distillation, and INT8 post-training quantization with
Hessian-aware block-wise reconstruction, taken all the way to TensorRT engines on NVIDIA
Jetson.

**[github.com/tommy0812/model-compression](https://github.com/tommy0812/model-compression)** —
a MobileViTv3 backbone compressed by **68% in parameters and 69% in MACs**, deployed as an INT8
TensorRT engine on Jetson AGX Orin at **0.864 ms** within **0.34 pp** of FP32 accuracy, with
96.6% of compute-bound layers running INT8 kernels.

A monocular depth network is the same class of target: an encoder–decoder whose cost is
dominated by convolutions and matrix multiplies that quantize well. The thesis established
what the depth system has to produce; the compression work is how it gets small enough to run
where it is needed.

---

## Reference

**Self-supervised Monocular Depth Estimation with Scale Recovery by Object Stereo Depth for
SLAM Application**
自監督單目深度估測與物件雙目深度校正融合之定位與地圖建構技術
M.S., Electrical and Control Engineering, National Yang Ming Chiao Tung University, January 2023.

**Keywords:** monocular depth estimation · self-supervised learning · metric scale recovery ·
stereo depth · instance segmentation · dense geometrical constraint · visual SLAM ·
ORB-SLAM2 · ROS · edge deployment

**Key references:** YolactEdge · Monodepth2 · DNet/DGC · ORB-SLAM2 · LeGO-LOAM · MS COCO

---

## Contact

[LinkedIn](https://linkedin.com/in/tommychen19920812) · a0912986300@gmail.com

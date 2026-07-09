# FaceShield Training

This directory contains the training code for the FaceShield algorithm module.

## Data Input

Training uses cropped face images and the clean manifest:

```text
data/ffpp_faces/
├─ face_manifest_clean.csv
├─ train/
│  ├─ real/
│  └─ fake/
├─ val/
│  ├─ real/
│  └─ fake/
└─ test/
   ├─ real/
   └─ fake/
```

The label convention is:

```text
real -> 0
fake -> 1
```

## Models

Four model types are supported:

```text
baseline   : RGB face crop -> lightweight CNN -> classifier
fusion_fft : RGB branch + FFT spectrum branch -> feature concat -> classifier
fusion_v2  : RGB branch + high-frequency FFT branch -> gated residual fusion -> classifier
fusion_v3  : RGB branch + DCT low/mid/high bands -> gated residual fusion -> classifier
```

`fusion_fft` is the first MVP model for the frequency-spatial fusion design.
`fusion_v2` is the optimized fusion model. It suppresses the low-frequency FFT
center region and uses a gate to control how much frequency feature is injected
into the spatial feature.
`fusion_v3` is a DCT-based follow-up experiment inspired by frequency-band
fusion papers. It uses fixed low/mid/high DCT bands as a lightweight substitute
for dynamic frequency partitioning.

## AutoDL Setup

Use a PaddlePaddle GPU image. For the RTX 3080 Ti configuration, the existing
`PaddlePaddle 2.4.0 / Python 3.8 / CUDA 11.2` image is acceptable.

Install only lightweight extra packages:

```bash
cd /root/autodl-tmp/FaceShield
python -m pip install -r training/requirements-autodl.txt
```

Verify Paddle GPU:

```bash
python -c "import paddle; print(paddle.__version__); print(paddle.device.is_compiled_with_cuda()); print(paddle.device.get_device())"
nvidia-smi
```

## Train Baseline

```bash
cd /root/autodl-tmp/FaceShield
python training/train.py \
  --data-root data/ffpp_faces \
  --manifest face_manifest_clean.csv \
  --model baseline \
  --output-dir outputs/baseline \
  --device gpu \
  --epochs 30 \
  --batch-size 32 \
  --lr 1e-3
```

## Train Frequency-Spatial Fusion

```bash
cd /root/autodl-tmp/FaceShield
python training/train.py \
  --data-root data/ffpp_faces \
  --manifest face_manifest_clean.csv \
  --model fusion_fft \
  --output-dir outputs/fusion_fft \
  --device gpu \
  --epochs 30 \
  --batch-size 32 \
  --lr 1e-3
```

## Train Optimized Frequency-Spatial Fusion

Use the trained baseline checkpoint to initialize the spatial branch. Freezing it
for the first few epochs lets the high-frequency branch and fusion head learn a
stable supplement before full fine-tuning.

```bash
cd /root/autodl-tmp/FaceShield
python training/train.py \
  --data-root data/ffpp_faces \
  --manifest face_manifest_clean.csv \
  --model fusion_v2 \
  --output-dir outputs/fusion_v2 \
  --device gpu \
  --epochs 30 \
  --batch-size 32 \
  --lr 5e-4 \
  --spatial-checkpoint outputs/baseline/best.pdparams \
  --freeze-spatial-epochs 3
```

## Train DCT Frequency-Spatial Fusion

This is the recommended next experiment after `fusion_v2`. It keeps the same
gated residual fusion structure, but replaces the high-frequency FFT input with
three DCT frequency bands.

```bash
cd /root/autodl-tmp/FaceShield
python training/train.py \
  --data-root data/ffpp_faces \
  --manifest face_manifest_clean.csv \
  --model fusion_v3 \
  --output-dir outputs/fusion_v3_seed42 \
  --device gpu \
  --epochs 30 \
  --batch-size 32 \
  --lr 5e-4 \
  --seed 42 \
  --spatial-checkpoint outputs/baseline/best.pdparams \
  --freeze-spatial-epochs 3
```

The training script writes:

```text
outputs/<run>/
├─ config.json
├─ history.json
├─ best.pdparams
├─ best_metrics.json
└─ test_metrics.json
```

## Single Image Check

```bash
python training/predict.py \
  --image data/ffpp_faces/test/fake/035_036_000001.jpg \
  --checkpoint model/deploy/fusion_v2/best.pdparams \
  --config model/deploy/fusion_v2/config.json \
  --device gpu
```

For backend development, use `model/deploy/fusion_v2` as the primary checkpoint
directory. `model/deploy/baseline` is kept as a fallback model.

## JPEG Robustness Evaluation

The robustness script evaluates deployed checkpoints on the test split after
in-memory JPEG re-encoding. It does not modify the original test images.

```powershell
.\.venv\Scripts\python.exe training\evaluate_jpeg_robustness.py `
  --output-dir model\robustness\jpeg `
  --qualities 95 75 50 30 `
  --batch-size 32 `
  --device cpu
```

By default, the script evaluates valid checkpoint directories under:

```text
model/deploy/baseline
model/deploy/fusion_v2
model/deploy/fusion_v3
```

If a model directory is missing, it is skipped. To evaluate another checkpoint,
pass `--model-dir <path>` one or more times. The output directory contains:

```text
metrics_by_quality.csv
metrics_by_quality.json
predictions_by_quality.csv
summary.md
```

## Grad-CAM Visualization

Use `gradcam.py` to generate an explainability heatmap for one cropped face
image. The heatmap is computed on the RGB spatial branch and overlaid on the
input image. For fusion models, the frequency branch still participates in the
classification score, but the displayed heatmap coordinates come from the RGB
branch so they can be interpreted on the face image.

```powershell
.\.venv\Scripts\python.exe training\gradcam.py `
  --image data\ffpp_faces\test\fake\035_036_000001.jpg `
  --checkpoint model\deploy\fusion_v2\best.pdparams `
  --config model\deploy\fusion_v2\config.json `
  --output-dir model\gradcam\fusion_v2_fake_demo `
  --target-class fake `
  --device cpu
```

The script writes:

```text
model/gradcam/<run>/
├─ input.jpg
├─ heatmap.jpg
├─ overlay.jpg
└─ result.json
```

`overlay.jpg` is the recommended frontend display image. The heatmap indicates
model attention for the selected class; it is not a pixel-level manipulation
mask.

## Threshold Evaluation

Use `evaluate_thresholds.py` to test different fake-probability decision
thresholds from saved per-image predictions. This does not rerun inference.

```powershell
.\.venv\Scripts\python.exe training\evaluate_thresholds.py `
  --predictions model\robustness\jpeg\predictions_by_quality.csv `
  --model fusion_v2 `
  --quality original `
  --output-dir model\thresholds\fusion_v2_original
```

The script writes:

```text
model/thresholds/fusion_v2_original/
├─ metrics_by_threshold.csv
├─ metrics_by_threshold.json
└─ summary.md
```

For the current `fusion_v2` test predictions, threshold `0.35` gives the best
F1 in the scanned range and improves fake recall compared with the default
`0.50` threshold, but it also increases false positives. FaceShield keeps
`0.50` as the binary `label` threshold and uses the threshold scan to define
display-only risk levels: `<0.35` low, `0.35-0.80` medium, `>=0.80` high.

## Cross-Domain Evaluation

Use `evaluate_cross_domain.py` to evaluate deployed checkpoints on data that was
not used for training. The current priority is:

```text
Plan A: FaceForensics++ original + FaceSwap/Face2Face test split
Plan B: Celeb-DF v2 test videos
```

For FaceForensics++ FaceSwap:

```powershell
.\.venv\Scripts\python.exe tools\extract_ffpp_frames.py `
  --fake-method FaceSwap `
  --output-dir data\ffpp_frames_faceswap `
  --compression c23 `
  --frame-interval 20

.\.venv\Scripts\python.exe tools\extract_faces.py `
  --input-manifest data\ffpp_frames_faceswap\manifest.csv `
  --frames-root data\ffpp_frames_faceswap `
  --output-dir data\ffpp_faces_faceswap

.\.venv\Scripts\python.exe training\evaluate_cross_domain.py `
  --data-root data\ffpp_faces_faceswap `
  --manifest face_manifest.csv `
  --split test `
  --domain-name ffpp_faceswap `
  --model-dir model\deploy\fusion_v2 `
  --output-dir model\cross_domain\ffpp_faceswap `
  --device cpu
```

For Celeb-DF v2:

```powershell
.\.venv\Scripts\python.exe tools\extract_celebdf_frames.py `
  --dataset-root data\Celeb-DF-v2 `
  --output-dir data\celebdf_frames `
  --frame-interval 20

.\.venv\Scripts\python.exe tools\extract_faces.py `
  --input-manifest data\celebdf_frames\manifest.csv `
  --frames-root data\celebdf_frames `
  --output-dir data\celebdf_faces

.\.venv\Scripts\python.exe training\evaluate_cross_domain.py `
  --data-root data\celebdf_faces `
  --manifest face_manifest.csv `
  --split test `
  --domain-name celebdf_v2 `
  --model-dir model\deploy\fusion_v2 `
  --output-dir model\cross_domain\celebdf_v2 `
  --device cpu
```

The evaluator writes `metrics.json`, `metrics.csv`, `group_summary.csv`,
`predictions.csv`, and `summary.md`.

## Upload Scope

Only these are required on AutoDL:

```text
training/
data/ffpp_faces/face_manifest_clean.csv
data/ffpp_faces/train/
data/ffpp_faces/val/
data/ffpp_faces/test/
```

Do not upload raw videos or original extracted frames for training.

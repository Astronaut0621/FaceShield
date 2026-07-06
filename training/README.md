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

Three model types are supported:

```text
baseline   : RGB face crop -> lightweight CNN -> classifier
fusion_fft : RGB branch + FFT spectrum branch -> feature concat -> classifier
fusion_v2  : RGB branch + high-frequency FFT branch -> gated residual fusion -> classifier
```

`fusion_fft` is the first MVP model for the frequency-spatial fusion design.
`fusion_v2` is the optimized fusion model. It suppresses the low-frequency FFT
center region and uses a gate to control how much frequency feature is injected
into the spatial feature.

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

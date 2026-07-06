# FaceShield Model Artifacts

This directory stores the deployment-ready model files used by the backend.

## Recommended Model

Use `deploy/fusion_v2` as the primary detector:

```text
model/deploy/fusion_v2/
+-- best.pdparams
+-- config.json
+-- best_metrics.json
+-- test_metrics.json
```

`fusion_v2` is the current frequency-spatial fusion model. It uses an RGB
spatial branch and a high-frequency FFT branch with gated residual fusion.

Seed 42 test metrics:

| Metric | Value |
|---|---:|
| Accuracy | 0.8333 |
| AUC | 0.9014 |
| Precision | 0.8259 |
| Recall | 0.8440 |
| F1 | 0.8348 |

## Baseline Model

`deploy/baseline` is kept as a fallback and comparison model:

```text
model/deploy/baseline/
+-- best.pdparams
+-- config.json
+-- best_metrics.json
+-- test_metrics.json
```

## Backend Usage

For single-image inference with the current training script:

```bash
python training/predict.py \
  --image data/ffpp_faces/test/fake/035_036_000001.jpg \
  --checkpoint model/deploy/fusion_v2/best.pdparams \
  --config model/deploy/fusion_v2/config.json \
  --device gpu
```

For CPU-only backend development, use `--device cpu`.

## Local Training Outputs

Full training runs remain local under `model/outputs/` and are ignored by Git.
Only `model/deploy/` is intended to be committed for teammates.

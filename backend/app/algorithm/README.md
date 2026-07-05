# FaceShield Algorithm Framework

The algorithm package is a framework boundary, not a real model implementation.

## Stable Entry

Backend services should only call:

```python
predict_image(image_path: str) -> dict
```

## Layers

```text
contracts/    Input/output dataclasses and engine protocol
models/       Engine implementations and registry
pipeline/     Validation, preprocess, feature extraction, inference, postprocess stages
postprocess/  Output artifact helpers such as heatmap URL mapping
resources/    Placeholder for model metadata or local model files
```

To add a real model later, create a new engine class implementing `DetectionEngine`, register it in `models/registry.py`, then set `FACESHIELD_ALGORITHM_BACKEND`.


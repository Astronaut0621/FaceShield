from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
import paddle
import paddle.nn.functional as F

from dataset import compute_frequency_tensor, pil_to_rgb_tensor
from models import build_model, is_fusion_model


CLASS_TO_INDEX = {"real": 0, "fake": 1}
INDEX_TO_CLASS = {0: "real", 1: "fake"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Grad-CAM heatmap for one face image.")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, default=Path("model/deploy/fusion_v2/best.pdparams"))
    parser.add_argument("--config", type=Path, default=Path("model/deploy/fusion_v2/config.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("model/gradcam/demo"))
    parser.add_argument("--model", choices=["baseline", "fusion_fft", "fusion_v2", "fusion_v3"], default=None)
    parser.add_argument("--image-size", type=int, default=None)
    parser.add_argument("--dropout", type=float, default=None)
    parser.add_argument("--feature-dim", type=int, default=None)
    parser.add_argument("--target-class", choices=["fake", "real", "predicted"], default="fake")
    parser.add_argument("--alpha", type=float, default=0.55, help="Maximum heatmap opacity on overlay.")
    parser.add_argument("--device", choices=["gpu", "cpu"], default="cpu")
    return parser.parse_args()


def risk_level(fake_probability: float) -> str:
    if fake_probability < 0.35:
        return "low"
    if fake_probability < 0.8:
        return "medium"
    return "high"


def load_config(config_path: Path | None) -> dict:
    if config_path and config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}


def preprocess_image(image_path: Path, image_size: int) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    if image.size != (image_size, image_size):
        image = image.resize((image_size, image_size), Image.BILINEAR)
    return image


def pool_backbone_feature(backbone, activation: paddle.Tensor) -> paddle.Tensor:
    pooled = backbone.pool(activation)
    return paddle.flatten(pooled, start_axis=1)


def forward_with_spatial_activation(
    model: paddle.nn.Layer,
    model_name: str,
    rgb: paddle.Tensor,
    frequency: paddle.Tensor | None,
) -> tuple[paddle.Tensor, paddle.Tensor]:
    if model_name == "baseline":
        activation = model.backbone.features(rgb)
        activation.retain_grads()
        spatial = pool_backbone_feature(model.backbone, activation)
        logits = model.classifier(spatial)
        return logits, activation

    if not is_fusion_model(model_name):
        raise ValueError(f"Unsupported Grad-CAM model: {model_name}")
    if frequency is None:
        raise ValueError(f"Frequency tensor is required for model: {model_name}")

    activation = model.spatial_branch.features(rgb)
    activation.retain_grads()
    spatial = pool_backbone_feature(model.spatial_branch, activation)
    frequency_feature = model.frequency_branch(frequency)

    if model_name == "fusion_fft":
        fused = paddle.concat([spatial, frequency_feature], axis=1)
        logits = model.classifier(fused)
        return logits, activation

    gate = model.gate(paddle.concat([spatial, frequency_feature], axis=1))
    fused = spatial + model.frequency_scale * gate * frequency_feature
    logits = model.classifier(fused)
    return logits, activation


def normalize_cam(cam: np.ndarray) -> np.ndarray:
    cam = np.maximum(cam, 0.0)
    max_value = float(cam.max())
    min_value = float(cam.min())
    if max_value <= min_value:
        return np.zeros_like(cam, dtype="float32")
    return ((cam - min_value) / (max_value - min_value)).astype("float32")


def compute_gradcam(
    model: paddle.nn.Layer,
    model_name: str,
    image: Image.Image,
    target_class: str,
) -> tuple[np.ndarray, dict[str, float | str]]:
    rgb = paddle.to_tensor(pil_to_rgb_tensor(image)).unsqueeze(0)
    rgb.stop_gradient = False
    frequency = None
    if is_fusion_model(model_name):
        frequency_np = compute_frequency_tensor(image, model_name)
        frequency = paddle.to_tensor(frequency_np).unsqueeze(0)
        frequency.stop_gradient = False

    model.clear_gradients()
    logits, activation = forward_with_spatial_activation(model, model_name, rgb, frequency)
    probability = F.softmax(logits, axis=1)
    probability_np = probability.numpy()[0]
    predicted_index = int(probability_np.argmax())
    target_index = predicted_index if target_class == "predicted" else CLASS_TO_INDEX[target_class]

    score = logits[:, target_index].sum()
    score.backward()

    gradients = activation.grad.numpy()[0]
    activations = activation.numpy()[0]
    weights = gradients.mean(axis=(1, 2))
    cam = np.sum(weights[:, np.newaxis, np.newaxis] * activations, axis=0)
    cam = normalize_cam(cam)

    cam_image = Image.fromarray(np.uint8(cam * 255), mode="L")
    cam_image = cam_image.resize(image.size, Image.BILINEAR)
    cam = np.asarray(cam_image, dtype="float32") / 255.0

    result = {
        "target_class": INDEX_TO_CLASS[target_index],
        "predicted_label": INDEX_TO_CLASS[predicted_index],
        "real_probability": float(probability_np[0]),
        "fake_probability": float(probability_np[1]),
        "risk_level": risk_level(float(probability_np[1])),
    }
    return cam, result


def colorize_cam(cam: np.ndarray) -> np.ndarray:
    x = np.clip(cam.astype("float32"), 0.0, 1.0)
    red = np.clip(1.5 - np.abs(4.0 * x - 3.0), 0.0, 1.0)
    green = np.clip(1.5 - np.abs(4.0 * x - 2.0), 0.0, 1.0)
    blue = np.clip(1.5 - np.abs(4.0 * x - 1.0), 0.0, 1.0)
    return np.stack([red, green, blue], axis=-1)


def build_overlay(image: Image.Image, cam: np.ndarray, alpha: float) -> tuple[Image.Image, Image.Image]:
    base = np.asarray(image.convert("RGB"), dtype="float32") / 255.0
    heatmap = colorize_cam(cam)
    alpha_map = np.clip(cam[..., np.newaxis] * alpha, 0.0, 1.0)
    overlay = base * (1.0 - alpha_map) + heatmap * alpha_map
    heatmap_image = Image.fromarray(np.uint8(np.clip(heatmap, 0.0, 1.0) * 255))
    overlay_image = Image.fromarray(np.uint8(np.clip(overlay, 0.0, 1.0) * 255))
    return heatmap_image, overlay_image


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    model_name = args.model or config.get("model") or "fusion_v2"
    image_size = args.image_size or int(config.get("image_size", 224))
    dropout = args.dropout if args.dropout is not None else float(config.get("dropout", 0.3))
    feature_dim = args.feature_dim or int(config.get("feature_dim", 128))

    if args.device == "gpu" and paddle.device.is_compiled_with_cuda():
        paddle.set_device("gpu")
    else:
        paddle.set_device("cpu")

    model = build_model(model_name, dropout=dropout, feature_dim=feature_dim)
    model.set_state_dict(paddle.load(str(args.checkpoint)))
    model.eval()

    image = preprocess_image(args.image, image_size)
    cam, result = compute_gradcam(model, model_name, image, args.target_class)
    heatmap, overlay = build_overlay(image, cam, args.alpha)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_path = args.output_dir / "input.jpg"
    heatmap_path = args.output_dir / "heatmap.jpg"
    overlay_path = args.output_dir / "overlay.jpg"
    result_path = args.output_dir / "result.json"

    image.save(input_path, quality=95)
    heatmap.save(heatmap_path, quality=95)
    overlay.save(overlay_path, quality=95)

    output = {
        "image": str(args.image),
        "model": model_name,
        "checkpoint": str(args.checkpoint),
        "config": str(args.config) if args.config else None,
        "target_class_mode": args.target_class,
        "spatial_cam_note": "Grad-CAM is computed on the RGB spatial branch last feature map.",
        "input_image": str(input_path),
        "heatmap_image": str(heatmap_path),
        "overlay_image": str(overlay_path),
        **result,
    }
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

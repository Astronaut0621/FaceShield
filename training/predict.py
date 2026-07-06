from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image
import paddle
import paddle.nn.functional as F

from dataset import compute_frequency_tensor, pil_to_rgb_tensor
from models import build_model, is_fusion_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FaceShield model on one cropped face image.")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=None)
    parser.add_argument("--model", choices=["baseline", "fusion_fft", "fusion_v2", "fusion_v3"], default=None)
    parser.add_argument("--image-size", type=int, default=None)
    parser.add_argument("--dropout", type=float, default=None)
    parser.add_argument("--feature-dim", type=int, default=None)
    parser.add_argument("--device", choices=["gpu", "cpu"], default="gpu")
    return parser.parse_args()


def risk_level(fake_probability: float) -> str:
    if fake_probability < 0.4:
        return "low"
    if fake_probability < 0.7:
        return "medium"
    return "high"


def main() -> int:
    args = parse_args()
    config = {}
    if args.config and args.config.exists():
        config = json.loads(args.config.read_text(encoding="utf-8"))

    model_name = args.model or config.get("model") or "fusion_fft"
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

    image = Image.open(args.image).convert("RGB")
    if image.size != (image_size, image_size):
        image = image.resize((image_size, image_size), Image.BILINEAR)
    rgb = paddle.to_tensor(pil_to_rgb_tensor(image)).unsqueeze(0)
    with paddle.no_grad():
        if is_fusion_model(model_name):
            frequency = paddle.to_tensor(compute_frequency_tensor(image, model_name)).unsqueeze(0)
            logits = model(rgb, frequency)
        else:
            logits = model(rgb)
        prob = F.softmax(logits, axis=1).numpy()[0]

    fake_probability = float(prob[1])
    result = {
        "image": str(args.image),
        "model": model_name,
        "real_probability": float(prob[0]),
        "fake_probability": fake_probability,
        "predicted_label": "fake" if fake_probability >= 0.5 else "real",
        "risk_level": risk_level(fake_probability),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

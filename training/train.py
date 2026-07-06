from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Optional

import numpy as np
import paddle
import paddle.nn.functional as F
from paddle.io import DataLoader
from tqdm import tqdm

from dataset import FaceForgeryDataset, read_manifest, split_rows
from metrics import classification_metrics
from models import build_model, is_fusion_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train FaceShield face forgery detector.")
    parser.add_argument("--data-root", type=Path, default=Path("data/ffpp_faces"))
    parser.add_argument("--manifest", default="face_manifest_clean.csv")
    parser.add_argument("--model", choices=["baseline", "fusion_fft", "fusion_v2", "fusion_v3"], default="fusion_fft")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/fusion_fft"))
    parser.add_argument("--device", choices=["gpu", "cpu"], default="gpu")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--dropout", type=float, default=0.3)
    parser.add_argument("--feature-dim", type=int, default=128)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-augment", action="store_true")
    parser.add_argument(
        "--spatial-checkpoint",
        type=Path,
        default=None,
        help="Optional baseline checkpoint used to initialize the spatial branch of fusion models.",
    )
    parser.add_argument(
        "--freeze-spatial-epochs",
        type=int,
        default=0,
        help="Freeze the initialized spatial branch for the first N epochs of fusion training.",
    )
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    paddle.seed(seed)


def make_loader(
    rows: list[dict[str, str]],
    data_root: Path,
    image_size: int,
    model_name: str,
    batch_size: int,
    shuffle: bool,
    augment: bool,
    num_workers: int,
) -> DataLoader:
    dataset = FaceForgeryDataset(
        rows=rows,
        data_root=data_root,
        image_size=image_size,
        mode=model_name if is_fusion_model(model_name) else "rgb",
        augment=augment,
    )
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        drop_last=False,
        return_list=True,
    )


def forward_model(model: paddle.nn.Layer, model_name: str, batch):
    if is_fusion_model(model_name):
        rgb, frequency, labels = batch
        logits = model(rgb, frequency)
    else:
        rgb, labels = batch
        logits = model(rgb)
    return logits, labels


def run_epoch(
    model: paddle.nn.Layer,
    loader: DataLoader,
    model_name: str,
    optimizer: Optional[paddle.optimizer.Optimizer],
    desc: str,
    freeze_spatial_branch: bool = False,
) -> dict[str, float]:
    is_train = optimizer is not None
    if is_train:
        model.train()
        if freeze_spatial_branch and hasattr(model, "spatial_branch"):
            model.spatial_branch.eval()
    else:
        model.eval()

    total_loss = 0.0
    total_samples = 0
    all_labels: list[int] = []
    all_probs: list[float] = []

    for batch in tqdm(loader, desc=desc, ncols=100):
        logits, labels = forward_model(model, model_name, batch)
        loss = F.cross_entropy(logits, labels)
        if is_train:
            loss.backward()
            optimizer.step()
            optimizer.clear_grad()

        probs = F.softmax(logits, axis=1)[:, 1]
        labels_np = labels.numpy().astype("int64")
        probs_np = probs.numpy().astype("float64")
        batch_size = int(labels_np.shape[0])
        total_loss += float(loss.numpy()) * batch_size
        total_samples += batch_size
        all_labels.extend(labels_np.tolist())
        all_probs.extend(probs_np.tolist())

    metrics = classification_metrics(all_labels, all_probs)
    metrics["loss"] = total_loss / total_samples if total_samples else 0.0
    return metrics


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_spatial_branch_from_baseline(model: paddle.nn.Layer, checkpoint_path: Path) -> int:
    if not hasattr(model, "spatial_branch"):
        raise ValueError("Spatial checkpoint can only be loaded into a fusion model.")
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Spatial checkpoint not found: {checkpoint_path}")

    baseline_state = paddle.load(str(checkpoint_path))
    model_state = model.state_dict()
    loaded = 0
    for key, value in baseline_state.items():
        if not key.startswith("backbone."):
            continue
        target_key = f"spatial_branch.{key[len('backbone.'):]}"
        if target_key in model_state and tuple(model_state[target_key].shape) == tuple(value.shape):
            model_state[target_key] = value
            loaded += 1
    model.set_state_dict(model_state)
    return loaded


def set_spatial_branch_trainable(model: paddle.nn.Layer, trainable: bool) -> None:
    if not hasattr(model, "spatial_branch"):
        return
    for parameter in model.spatial_branch.parameters():
        parameter.stop_gradient = not trainable


def main() -> int:
    args = parse_args()
    if args.spatial_checkpoint and not is_fusion_model(args.model):
        raise SystemExit("--spatial-checkpoint is only supported for fusion models.")
    if args.freeze_spatial_epochs > 0 and not args.spatial_checkpoint:
        raise SystemExit("--freeze-spatial-epochs requires --spatial-checkpoint.")

    set_seed(args.seed)
    if args.device == "gpu" and paddle.device.is_compiled_with_cuda():
        paddle.set_device("gpu")
    else:
        paddle.set_device("cpu")

    manifest_path = args.data_root / args.manifest
    rows = read_manifest(manifest_path)
    train_rows = split_rows(rows, "train")
    val_rows = split_rows(rows, "val")
    test_rows = split_rows(rows, "test")
    if not train_rows or not val_rows or not test_rows:
        raise SystemExit("Manifest must contain train, val and test rows.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args).copy()
    config["data_root"] = str(args.data_root)
    config["output_dir"] = str(args.output_dir)
    config["spatial_checkpoint"] = str(args.spatial_checkpoint) if args.spatial_checkpoint else None
    config["manifest_path"] = str(manifest_path)
    config["paddle_version"] = paddle.__version__
    config["device_used"] = paddle.device.get_device()
    config["split_sizes"] = {
        "train": len(train_rows),
        "val": len(val_rows),
        "test": len(test_rows),
    }
    save_json(args.output_dir / "config.json", config)

    train_loader = make_loader(
        train_rows,
        args.data_root,
        args.image_size,
        args.model,
        args.batch_size,
        shuffle=True,
        augment=not args.no_augment,
        num_workers=args.num_workers,
    )
    val_loader = make_loader(
        val_rows,
        args.data_root,
        args.image_size,
        args.model,
        args.batch_size,
        shuffle=False,
        augment=False,
        num_workers=args.num_workers,
    )
    test_loader = make_loader(
        test_rows,
        args.data_root,
        args.image_size,
        args.model,
        args.batch_size,
        shuffle=False,
        augment=False,
        num_workers=args.num_workers,
    )

    model = build_model(args.model, dropout=args.dropout, feature_dim=args.feature_dim)
    if args.spatial_checkpoint:
        loaded = load_spatial_branch_from_baseline(model, args.spatial_checkpoint)
        print(f"loaded {loaded} tensors into spatial_branch from {args.spatial_checkpoint}")
        if loaded == 0:
            raise SystemExit("No spatial branch tensors were loaded; check checkpoint compatibility.")
    if args.freeze_spatial_epochs > 0:
        set_spatial_branch_trainable(model, False)
        print(f"spatial_branch frozen for first {args.freeze_spatial_epochs} epochs")

    optimizer = paddle.optimizer.AdamW(
        learning_rate=args.lr,
        parameters=model.parameters(),
        weight_decay=args.weight_decay,
    )

    best_auc = -1.0
    best_epoch = 0
    no_improve = 0
    history = []
    started_at = time.time()
    for epoch in range(1, args.epochs + 1):
        if args.freeze_spatial_epochs > 0 and epoch == args.freeze_spatial_epochs + 1:
            set_spatial_branch_trainable(model, True)
            print("spatial_branch unfrozen")
        spatial_frozen = args.freeze_spatial_epochs > 0 and epoch <= args.freeze_spatial_epochs
        train_metrics = run_epoch(
            model,
            train_loader,
            args.model,
            optimizer,
            f"epoch {epoch} train",
            freeze_spatial_branch=spatial_frozen,
        )
        val_metrics = run_epoch(model, val_loader, args.model, None, f"epoch {epoch} val")
        record = {
            "epoch": epoch,
            "train": train_metrics,
            "val": val_metrics,
        }
        history.append(record)
        save_json(args.output_dir / "history.json", history)
        print(
            f"epoch={epoch} "
            f"train_loss={train_metrics['loss']:.4f} "
            f"train_acc={train_metrics['accuracy']:.4f} "
            f"val_loss={val_metrics['loss']:.4f} "
            f"val_acc={val_metrics['accuracy']:.4f} "
            f"val_auc={val_metrics['auc']:.4f}"
        )

        current_auc = val_metrics["auc"]
        if current_auc > best_auc:
            best_auc = current_auc
            best_epoch = epoch
            no_improve = 0
            paddle.save(model.state_dict(), str(args.output_dir / "best.pdparams"))
            save_json(args.output_dir / "best_metrics.json", {"epoch": epoch, "val": val_metrics})
        else:
            no_improve += 1
            if no_improve >= args.patience:
                print(f"early stopping at epoch {epoch}; best_epoch={best_epoch}")
                break

    best_path = args.output_dir / "best.pdparams"
    if best_path.exists():
        state = paddle.load(str(best_path))
        model.set_state_dict(state)
    test_metrics = run_epoch(model, test_loader, args.model, None, "test")
    summary = {
        "best_epoch": best_epoch,
        "best_val_auc": best_auc,
        "test": test_metrics,
        "elapsed_seconds": round(time.time() - started_at, 2),
    }
    save_json(args.output_dir / "test_metrics.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""Extract a FaceForensics++ video subset into image folders plus manifest.csv."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "data" / "FaceForensics-data"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "ffpp_frames"
DEFAULT_SPLITS_DIR = Path(r"D:\FaceForensics-master\dataset\splits")


def get_ffmpeg_exe() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
    except ImportError as exc:
        raise SystemExit(
            "ffmpeg was not found. Install imageio-ffmpeg with: "
            "python -m pip install imageio-ffmpeg"
        ) from exc
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_splits(splits_dir: Path) -> tuple[dict[str, str], dict[frozenset[str], str]]:
    id_to_split: dict[str, str] = {}
    pair_to_split: dict[frozenset[str], str] = {}
    for split in ("train", "val", "test"):
        split_file = splits_dir / f"{split}.json"
        if not split_file.exists():
            raise FileNotFoundError(f"Missing split file: {split_file}")
        pairs = json.loads(split_file.read_text(encoding="utf-8"))
        for pair in pairs:
            a, b = str(pair[0]), str(pair[1])
            pair_to_split[frozenset((a, b))] = split
            for video_id in (a, b):
                previous = id_to_split.get(video_id)
                if previous and previous != split:
                    raise ValueError(f"Video id {video_id} appears in {previous} and {split}")
                id_to_split[video_id] = split
    return id_to_split, pair_to_split


def split_for_real(video_path: Path, id_to_split: dict[str, str]) -> str:
    return id_to_split.get(video_path.stem, "unknown")


def split_for_fake(
    video_path: Path,
    id_to_split: dict[str, str],
    pair_to_split: dict[frozenset[str], str],
) -> str:
    parts = video_path.stem.split("_", 1)
    if len(parts) != 2:
        return "unknown"
    pair_key = frozenset(parts)
    if pair_key in pair_to_split:
        return pair_to_split[pair_key]
    split_a = id_to_split.get(parts[0])
    split_b = id_to_split.get(parts[1])
    if split_a and split_a == split_b:
        return split_a
    return "unknown"


def run_ffmpeg_extract(
    ffmpeg: str,
    video_path: Path,
    output_pattern: Path,
    frame_interval: int,
    jpeg_quality: int,
    resize: int,
) -> None:
    vf_parts = [f"select=not(mod(n\\,{frame_interval}))"]
    if resize:
        vf_parts.append(
            f"scale={resize}:{resize}:force_original_aspect_ratio=increase,"
            f"crop={resize}:{resize}"
        )
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-xerror",
        "-i",
        str(video_path),
        "-vf",
        ",".join(vf_parts),
        "-vsync",
        "vfr",
        "-q:v",
        str(jpeg_quality),
        str(output_pattern),
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {video_path}:\n{result.stderr.strip()}")


def collect_existing_frames(out_dir: Path, video_stem: str) -> list[Path]:
    return sorted(out_dir.glob(f"{video_stem}_*.jpg"))


def extract_video(
    ffmpeg: str,
    video_path: Path,
    split: str,
    label: int,
    label_name: str,
    method: str,
    output_dir: Path,
    frame_interval: int,
    jpeg_quality: int,
    resize: int,
    overwrite: bool,
) -> list[dict[str, str | int]]:
    out_dir = output_dir / split / label_name
    out_dir.mkdir(parents=True, exist_ok=True)
    video_stem = video_path.stem
    existing = collect_existing_frames(out_dir, video_stem)
    if existing and overwrite:
        for frame_path in existing:
            frame_path.unlink()
        existing = []

    if not existing:
        output_pattern = out_dir / f"{video_stem}_%06d.jpg"
        run_ffmpeg_extract(
            ffmpeg=ffmpeg,
            video_path=video_path,
            output_pattern=output_pattern,
            frame_interval=frame_interval,
            jpeg_quality=jpeg_quality,
            resize=resize,
        )

    frames = collect_existing_frames(out_dir, video_stem)
    rows: list[dict[str, str | int]] = []
    for ordinal, frame_path in enumerate(frames):
        rows.append(
            {
                "split": split,
                "label": label,
                "label_name": label_name,
                "method": method,
                "video": video_path.name,
                "video_stem": video_stem,
                "frame_ordinal": ordinal,
                "frame_interval": frame_interval,
                "image_path": str(frame_path.relative_to(output_dir).as_posix()),
                "source_video": str(video_path),
            }
        )
    return rows


def write_manifest(rows: list[dict[str, str | int]], manifest_path: Path) -> None:
    fieldnames = [
        "split",
        "label",
        "label_name",
        "method",
        "video",
        "video_stem",
        "frame_ordinal",
        "frame_interval",
        "image_path",
        "source_video",
    ]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract downloaded FaceForensics++ videos into train/val/test image folders."
    )
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--splits-dir", type=Path, default=DEFAULT_SPLITS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--compression", default="c23")
    parser.add_argument("--fake-method", default="Deepfakes")
    parser.add_argument("--frame-interval", type=int, default=20)
    parser.add_argument("--jpeg-quality", type=int, default=2, help="FFmpeg q:v, lower is better.")
    parser.add_argument("--resize", type=int, default=0, help="Optional square resize/crop size.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--allow-unknown-split", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.frame_interval <= 0:
        raise SystemExit("--frame-interval must be positive")
    if args.resize < 0:
        raise SystemExit("--resize cannot be negative")

    real_dir = args.dataset_root / "original_sequences" / "youtube" / args.compression / "videos"
    fake_dir = (
        args.dataset_root
        / "manipulated_sequences"
        / args.fake_method
        / args.compression
        / "videos"
    )
    if not real_dir.exists():
        raise FileNotFoundError(f"Missing real videos directory: {real_dir}")
    if not fake_dir.exists():
        raise FileNotFoundError(f"Missing fake videos directory: {fake_dir}")

    id_to_split, pair_to_split = load_splits(args.splits_dir)
    ffmpeg = get_ffmpeg_exe()
    rows: list[dict[str, str | int]] = []

    jobs: list[tuple[Path, str, int, str, str]] = []
    for video_path in sorted(real_dir.glob("*.mp4")):
        jobs.append((video_path, split_for_real(video_path, id_to_split), 0, "real", "original"))
    for video_path in sorted(fake_dir.glob("*.mp4")):
        jobs.append(
            (
                video_path,
                split_for_fake(video_path, id_to_split, pair_to_split),
                1,
                "fake",
                args.fake_method,
            )
        )

    unknown = [video_path.name for video_path, split, *_ in jobs if split == "unknown"]
    if unknown and not args.allow_unknown_split:
        raise SystemExit(
            "Some videos are not covered by the official split files: "
            + ", ".join(unknown[:20])
        )

    print(f"ffmpeg: {ffmpeg}")
    print(f"videos: {len(jobs)}")
    print(f"output: {args.output_dir}")
    for idx, (video_path, split, label, label_name, method) in enumerate(jobs, start=1):
        print(f"[{idx:03d}/{len(jobs):03d}] {split}/{label_name}: {video_path.name}")
        rows.extend(
            extract_video(
                ffmpeg=ffmpeg,
                video_path=video_path,
                split=split,
                label=label,
                label_name=label_name,
                method=method,
                output_dir=args.output_dir,
                frame_interval=args.frame_interval,
                jpeg_quality=args.jpeg_quality,
                resize=args.resize,
                overwrite=args.overwrite,
            )
        )

    manifest_path = args.output_dir / "manifest.csv"
    write_manifest(rows, manifest_path)
    print(f"manifest: {manifest_path}")
    print(f"frames: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

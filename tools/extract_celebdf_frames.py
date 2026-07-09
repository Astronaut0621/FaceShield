#!/usr/bin/env python
"""Extract Celeb-DF v2 videos into image folders plus manifest.csv."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = PROJECT_ROOT / "data" / "Celeb-DF-v2"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "celebdf_frames"


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


def normalize_rel_path(value: str) -> str:
    return value.strip().replace("\\", "/")


def infer_label(rel_path: str) -> tuple[int, str, str]:
    top = normalize_rel_path(rel_path).split("/", 1)[0]
    lower_top = top.lower()
    if "synthesis" in lower_top or "fake" in lower_top:
        return 1, "fake", top
    if "real" in lower_top or "youtube" in lower_top:
        return 0, "real", top
    raise ValueError(f"Cannot infer real/fake label from Celeb-DF path: {rel_path}")


def parse_list_file(list_file: Path) -> list[str]:
    rel_paths: list[str] = []
    for line in list_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0] in {"0", "1"}:
            rel_paths.append(normalize_rel_path(parts[1]))
        else:
            rel_paths.append(normalize_rel_path(parts[0]))
    return rel_paths


def collect_videos(args: argparse.Namespace) -> list[tuple[Path, str, str, int, str, str]]:
    list_file = args.list_file
    if list_file is None:
        candidate = args.dataset_root / "List_of_testing_videos.txt"
        list_file = candidate if candidate.exists() else None

    jobs: list[tuple[Path, str, str, int, str, str]] = []
    missing: list[str] = []
    if list_file is not None and not args.all_videos:
        rel_paths = parse_list_file(list_file)
        for rel_path in rel_paths:
            label, label_name, method = infer_label(rel_path)
            video_path = args.dataset_root / rel_path
            if not video_path.exists():
                missing.append(rel_path)
                continue
            jobs.append((video_path, rel_path, "test", label, label_name, method))
    else:
        for video_path in sorted(args.dataset_root.rglob("*.mp4")):
            rel_path = video_path.relative_to(args.dataset_root).as_posix()
            label, label_name, method = infer_label(rel_path)
            jobs.append((video_path, rel_path, args.split, label, label_name, method))

    if missing and not args.allow_missing_listed:
        raise FileNotFoundError(
            "Some listed Celeb-DF videos are missing: " + ", ".join(missing[:20])
        )
    if args.max_videos and args.max_videos > 0:
        jobs = jobs[: args.max_videos]
    return jobs


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


def safe_video_id(rel_path: str) -> str:
    return Path(normalize_rel_path(rel_path)).with_suffix("").as_posix().replace("/", "__")


def collect_existing_frames(out_dir: Path, video_id: str) -> list[Path]:
    return sorted(out_dir.glob(f"{video_id}_*.jpg"))


def extract_video(
    ffmpeg: str,
    video_path: Path,
    rel_path: str,
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
    video_id = safe_video_id(rel_path)
    existing = collect_existing_frames(out_dir, video_id)
    if existing and overwrite:
        for frame_path in existing:
            frame_path.unlink()
        existing = []

    if not existing:
        output_pattern = out_dir / f"{video_id}_%06d.jpg"
        run_ffmpeg_extract(
            ffmpeg=ffmpeg,
            video_path=video_path,
            output_pattern=output_pattern,
            frame_interval=frame_interval,
            jpeg_quality=jpeg_quality,
            resize=resize,
        )

    frames = collect_existing_frames(out_dir, video_id)
    rows: list[dict[str, str | int]] = []
    for ordinal, frame_path in enumerate(frames):
        rows.append(
            {
                "split": split,
                "label": label,
                "label_name": label_name,
                "method": method,
                "video": video_path.name,
                "video_stem": video_id,
                "video_rel_path": rel_path,
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
        "video_rel_path",
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
        description="Extract Celeb-DF v2 videos into test image folders."
    )
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--list-file", type=Path, default=None)
    parser.add_argument("--all-videos", action="store_true")
    parser.add_argument("--split", default="test", choices=["train", "val", "test"])
    parser.add_argument("--frame-interval", type=int, default=20)
    parser.add_argument("--jpeg-quality", type=int, default=2, help="FFmpeg q:v, lower is better.")
    parser.add_argument("--resize", type=int, default=0, help="Optional square resize/crop size.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--max-videos", type=int, default=0)
    parser.add_argument("--allow-missing-listed", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.frame_interval <= 0:
        raise SystemExit("--frame-interval must be positive")
    if args.resize < 0:
        raise SystemExit("--resize cannot be negative")
    if not args.dataset_root.exists():
        raise FileNotFoundError(f"Missing Celeb-DF dataset root: {args.dataset_root}")

    ffmpeg = get_ffmpeg_exe()
    jobs = collect_videos(args)
    if not jobs:
        raise SystemExit("No Celeb-DF videos found.")

    rows: list[dict[str, str | int]] = []
    print(f"ffmpeg: {ffmpeg}")
    print(f"videos: {len(jobs)}")
    print(f"output: {args.output_dir}")
    for idx, (video_path, rel_path, split, label, label_name, method) in enumerate(jobs, start=1):
        print(f"[{idx:04d}/{len(jobs):04d}] {split}/{label_name}: {rel_path}")
        rows.extend(
            extract_video(
                ffmpeg=ffmpeg,
                video_path=video_path,
                rel_path=rel_path,
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

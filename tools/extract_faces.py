#!/usr/bin/env python
"""Create face crops from extracted FaceForensics++ frames."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_MANIFEST = PROJECT_ROOT / "data" / "ffpp_frames" / "manifest.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "ffpp_faces"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect and crop faces from ffpp_frames images."
    )
    parser.add_argument("--input-manifest", type=Path, default=DEFAULT_INPUT_MANIFEST)
    parser.add_argument("--frames-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--size", type=int, default=224)
    parser.add_argument("--expand", type=float, default=1.3)
    parser.add_argument("--scale-factor", type=float, default=1.1)
    parser.add_argument("--min-neighbors", type=int, default=5)
    parser.add_argument("--min-face-size", type=int, default=40)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--cascade", type=Path, default=None)
    return parser.parse_args()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_detector(cascade_path: Path | None) -> tuple[cv2.CascadeClassifier, Path]:
    if cascade_path is None:
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        raise FileNotFoundError(f"Could not load Haar cascade: {cascade_path}")
    return detector, cascade_path


def square_from_bbox(
    x: int,
    y: int,
    w: int,
    h: int,
    image_w: int,
    image_h: int,
    expand: float,
) -> tuple[int, int, int, int]:
    side = int(round(max(w, h) * expand))
    side = max(1, min(side, image_w, image_h))
    cx = x + w / 2.0
    cy = y + h / 2.0
    x1 = int(round(cx - side / 2.0))
    y1 = int(round(cy - side / 2.0))
    x2 = x1 + side
    y2 = y1 + side
    if x1 < 0:
        x2 -= x1
        x1 = 0
    if y1 < 0:
        y2 -= y1
        y1 = 0
    if x2 > image_w:
        shift = x2 - image_w
        x1 -= shift
        x2 = image_w
    if y2 > image_h:
        shift = y2 - image_h
        y1 -= shift
        y2 = image_h
    x1 = max(0, x1)
    y1 = max(0, y1)
    return x1, y1, x2, y2


def center_square(image_w: int, image_h: int) -> tuple[int, int, int, int]:
    side = min(image_w, image_h)
    x1 = (image_w - side) // 2
    y1 = (image_h - side) // 2
    return x1, y1, x1 + side, y1 + side


def detect_largest_face(
    image,
    detector: cv2.CascadeClassifier,
    scale_factor: float,
    min_neighbors: int,
    min_face_size: int,
) -> tuple[tuple[int, int, int, int] | None, int]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = detector.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(min_face_size, min_face_size),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    if len(faces) == 0:
        return None, 0
    largest = max(faces, key=lambda item: int(item[2]) * int(item[3]))
    return tuple(int(v) for v in largest), len(faces)


def output_path_for(output_dir: Path, row: dict[str, str]) -> Path:
    split = row["split"]
    label_name = row["label_name"]
    source_stem = Path(row["image_path"]).stem
    return output_dir / split / label_name / f"{source_stem}.jpg"


def write_manifest(rows: list[dict[str, str]], output_path: Path) -> None:
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_row(
    row: dict[str, str],
    frames_root: Path,
    output_dir: Path,
    detector: cv2.CascadeClassifier,
    detector_name: str,
    args: argparse.Namespace,
) -> dict[str, str]:
    source_path = frames_root / row["image_path"]
    face_path = output_path_for(output_dir, row)
    face_path.parent.mkdir(parents=True, exist_ok=True)

    out = dict(row)
    out.update(
        {
            "source_frame_path": row["image_path"],
            "face_image_path": str(face_path.relative_to(output_dir).as_posix()),
            "face_detected": "0",
            "fallback": "0",
            "face_count": "0",
            "bbox_x": "",
            "bbox_y": "",
            "bbox_w": "",
            "bbox_h": "",
            "crop_x1": "",
            "crop_y1": "",
            "crop_x2": "",
            "crop_y2": "",
            "crop_size": str(args.size),
            "detector": detector_name,
            "error": "",
        }
    )

    image = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
    if image is None:
        out["error"] = f"could not read source image: {source_path}"
        return out

    image_h, image_w = image.shape[:2]
    face, face_count = detect_largest_face(
        image=image,
        detector=detector,
        scale_factor=args.scale_factor,
        min_neighbors=args.min_neighbors,
        min_face_size=args.min_face_size,
    )
    out["face_count"] = str(face_count)
    if face is None:
        x1, y1, x2, y2 = center_square(image_w, image_h)
        out["fallback"] = "1"
    else:
        x, y, w, h = face
        out["face_detected"] = "1"
        out["bbox_x"] = str(x)
        out["bbox_y"] = str(y)
        out["bbox_w"] = str(w)
        out["bbox_h"] = str(h)
        x1, y1, x2, y2 = square_from_bbox(
            x=x,
            y=y,
            w=w,
            h=h,
            image_w=image_w,
            image_h=image_h,
            expand=args.expand,
        )

    out["crop_x1"] = str(x1)
    out["crop_y1"] = str(y1)
    out["crop_x2"] = str(x2)
    out["crop_y2"] = str(y2)
    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        out["error"] = "empty crop"
        return out

    crop = cv2.resize(crop, (args.size, args.size), interpolation=cv2.INTER_AREA)
    if args.overwrite or not face_path.exists():
        cv2.imwrite(str(face_path), crop, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    return out


def main() -> int:
    args = parse_args()
    if args.size <= 0:
        raise SystemExit("--size must be positive")
    if args.expand <= 0:
        raise SystemExit("--expand must be positive")
    if args.frames_root is None:
        args.frames_root = args.input_manifest.parent

    rows = read_manifest(args.input_manifest)
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    detector, cascade_path = load_detector(args.cascade)
    detector_name = str(cascade_path)
    print(f"input_manifest: {args.input_manifest}")
    print(f"frames_root: {args.frames_root}")
    print(f"output_dir: {args.output_dir}")
    print(f"detector: {detector_name}")
    print(f"rows: {len(rows)}")

    output_rows: list[dict[str, str]] = []
    detected = 0
    fallback = 0
    errors = 0
    for idx, row in enumerate(rows, start=1):
        out = process_row(
            row=row,
            frames_root=args.frames_root,
            output_dir=args.output_dir,
            detector=detector,
            detector_name=detector_name,
            args=args,
        )
        output_rows.append(out)
        detected += out["face_detected"] == "1"
        fallback += out["fallback"] == "1"
        errors += bool(out["error"])
        if idx % 200 == 0 or idx == len(rows):
            print(
                f"[{idx}/{len(rows)}] detected={detected} "
                f"fallback={fallback} errors={errors}"
            )

    manifest_path = args.output_dir / "face_manifest.csv"
    write_manifest(output_rows, manifest_path)
    print(f"face_manifest: {manifest_path}")
    print(f"detected: {detected}")
    print(f"fallback: {fallback}")
    print(f"errors: {errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""FaceShield desktop floating detection assistant.

This MVP samples a user-selected screen region, submits frames to the existing
FaceShield backend, and shows risk status in an always-on-top Tk window.
"""

from __future__ import annotations

import io
import json
import os
import sys
import threading
import time
import uuid
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageGrab, ImageTk


DEFAULT_API_BASE = os.getenv("FACESHIELD_API_BASE_URL", "http://127.0.0.1:8000/api")
DEFAULT_USERNAME = os.getenv("FACESHIELD_USERNAME", "demo")
DEFAULT_PASSWORD = os.getenv("FACESHIELD_PASSWORD", "demo123456")
DEFAULT_INTERVAL = float(os.getenv("FACESHIELD_CAPTURE_INTERVAL", "2.0"))


def enable_windows_dpi_awareness() -> None:
    """Keep Tk selection coordinates aligned with ImageGrab pixels on Windows."""
    if sys.platform != "win32":
        return

    try:
        import ctypes

        # Per-monitor DPI awareness v2. Fall back for older Windows versions.
        if ctypes.windll.user32.SetProcessDpiAwarenessContext(-4):
            return
    except Exception:
        pass

    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass

    try:
        import ctypes

        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


@dataclass(frozen=True)
class ScreenRegion:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return max(0, self.right - self.left)

    @property
    def height(self) -> int:
        return max(0, self.bottom - self.top)

    def as_bbox(self) -> tuple[int, int, int, int]:
        return (self.left, self.top, self.right, self.bottom)

    def is_valid(self) -> bool:
        return self.width >= 80 and self.height >= 80


class FaceShieldApiClient:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url.rstrip("/")
        self.token = ""

    def set_api_base_url(self, api_base_url: str) -> None:
        self.api_base_url = api_base_url.rstrip("/")

    def login(self, username: str, password: str) -> dict[str, Any]:
        payload = self._post_json("/auth/login", {"username": username, "password": password})
        self.token = str(payload.get("access_token") or "")
        if not self.token:
            raise RuntimeError("登录成功响应中没有 access_token。")
        return payload

    def detect_frame(self, image_bytes: bytes, model_id: str | None = None) -> dict[str, Any]:
        fields: dict[str, str] = {}
        if model_id:
            fields["model_id"] = model_id
        return self._post_multipart(
            "/detection/upload-and-detect",
            fields=fields,
            file_field="file",
            filename=f"floating_frame_{int(time.time())}.jpg",
            file_bytes=image_bytes,
            content_type="image/jpeg",
        )

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        return self._request(path, data=data, headers={"Content-Type": "application/json"}, method="POST")

    def _post_multipart(
        self,
        path: str,
        fields: dict[str, str],
        file_field: str,
        filename: str,
        file_bytes: bytes,
        content_type: str,
    ) -> dict[str, Any]:
        boundary = f"----FaceShieldBoundary{uuid.uuid4().hex}"
        body = io.BytesIO()

        for name, value in fields.items():
            body.write(f"--{boundary}\r\n".encode("utf-8"))
            body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            body.write(str(value).encode("utf-8"))
            body.write(b"\r\n")

        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(
            (
                f'Content-Disposition: form-data; name="{file_field}"; '
                f'filename="{filename}"\r\n'
                f"Content-Type: {content_type}\r\n\r\n"
            ).encode("utf-8")
        )
        body.write(file_bytes)
        body.write(b"\r\n")
        body.write(f"--{boundary}--\r\n".encode("utf-8"))

        return self._request(
            path,
            data=body.getvalue(),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )

    def _request(
        self,
        path: str,
        data: bytes,
        headers: dict[str, str] | None = None,
        method: str = "POST",
    ) -> dict[str, Any]:
        url = f"{self.api_base_url}{path}"
        request_headers = dict(headers or {})
        if self.token:
            request_headers["Authorization"] = f"Bearer {self.token}"

        request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"无法连接后端：{exc.reason}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"后端返回不是 JSON：{raw[:120]}") from exc

        if isinstance(payload, dict) and payload.get("code") not in (None, 200):
            raise RuntimeError(str(payload.get("message") or "检测请求失败。"))
        return payload.get("data") if isinstance(payload, dict) else payload


class RegionSelector:
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.region: ScreenRegion | None = None
        self.start_x = 0
        self.start_y = 0
        self.start_x_root = 0
        self.start_y_root = 0
        self.rect_id: int | None = None

    def select(self) -> ScreenRegion | None:
        overlay = tk.Toplevel(self.parent)
        overlay.title("FaceShield 区域选择")
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.28)
        overlay.configure(cursor="crosshair", bg="#0f172a")

        canvas = tk.Canvas(overlay, bg="#0f172a", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(
            28,
            28,
            anchor="nw",
            text="拖拽框选视频人脸区域，松开鼠标确认；按 Esc 取消",
            fill="white",
            font=("Microsoft YaHei", 16, "bold"),
        )

        def on_press(event: tk.Event) -> None:
            self.start_x = int(event.x)
            self.start_y = int(event.y)
            self.start_x_root = int(event.x_root)
            self.start_y_root = int(event.y_root)
            if self.rect_id is not None:
                canvas.delete(self.rect_id)
            self.rect_id = canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                outline="#22d3ee",
                width=3,
            )

        def on_drag(event: tk.Event) -> None:
            if self.rect_id is not None:
                canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

        def on_release(event: tk.Event) -> None:
            left, right = sorted((self.start_x_root, int(event.x_root)))
            top, bottom = sorted((self.start_y_root, int(event.y_root)))
            self.region = ScreenRegion(left=left, top=top, right=right, bottom=bottom)
            overlay.destroy()

        def on_cancel(_: tk.Event | None = None) -> None:
            self.region = None
            overlay.destroy()

        overlay.bind("<ButtonPress-1>", on_press)
        overlay.bind("<B1-Motion>", on_drag)
        overlay.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", on_cancel)
        overlay.grab_set()
        self.parent.wait_window(overlay)
        return self.region


class FloatingAssistantApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.api_client = FaceShieldApiClient(DEFAULT_API_BASE)
        self.region: ScreenRegion | None = None
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.recent_high_flags: deque[bool] = deque(maxlen=5)

        self.api_var = tk.StringVar(value=DEFAULT_API_BASE)
        self.username_var = tk.StringVar(value=DEFAULT_USERNAME)
        self.password_var = tk.StringVar(value=DEFAULT_PASSWORD)
        self.model_id_var = tk.StringVar(value="")
        self.interval_var = tk.DoubleVar(value=DEFAULT_INTERVAL)
        self.region_var = tk.StringVar(value="未选择区域")
        self.status_var = tk.StringVar(value="待登录")
        self.risk_var = tk.StringVar(value="未检测")
        self.probability_var = tk.StringVar(value="--")
        self.last_time_var = tk.StringVar(value="--")
        self.preview_time_var = tk.StringVar(value="最近截帧：未开始")
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.preview_canvas: tk.Canvas | None = None

        self._setup_window()
        self._build_ui()
        self._apply_status("idle")

    def _setup_window(self) -> None:
        self.root.title("FaceShield 悬浮检测助手")
        self.root.geometry("380x780+80+80")
        self.root.minsize(360, 720)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#eef2f7")

    def _build_ui(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("Title.TLabel", background="#ffffff", foreground="#172033", font=("Microsoft YaHei", 15, "bold"))
        style.configure("Muted.TLabel", background="#ffffff", foreground="#647084", font=("Microsoft YaHei", 9))
        style.configure("Value.TLabel", background="#ffffff", foreground="#172033", font=("Microsoft YaHei", 20, "bold"))
        style.configure("Accent.TButton", font=("Microsoft YaHei", 10, "bold"))

        frame = ttk.Frame(self.root, style="Card.TFrame", padding=18)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        header = ttk.Frame(frame, style="Card.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="FaceShield", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="桌面悬浮检测助手", style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        self.risk_label = ttk.Label(frame, textvariable=self.risk_var, style="Value.TLabel")
        self.risk_label.pack(anchor="w", pady=(16, 2))
        ttk.Label(frame, textvariable=self.probability_var, style="Muted.TLabel").pack(anchor="w")
        ttk.Label(frame, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        form = ttk.Frame(frame, style="Card.TFrame")
        form.pack(fill="x", pady=(16, 0))
        self._add_entry(form, "后端 API", self.api_var, show=None)
        self._add_entry(form, "用户名", self.username_var, show=None)
        self._add_entry(form, "密码", self.password_var, show="*")
        self._add_entry(form, "模型 ID（可选）", self.model_id_var, show=None)

        row = ttk.Frame(form, style="Card.TFrame")
        row.pack(fill="x", pady=(8, 0))
        ttk.Label(row, text="检测间隔（秒）", style="Muted.TLabel").pack(side="left")
        interval = ttk.Spinbox(row, from_=1.0, to=10.0, increment=0.5, textvariable=self.interval_var, width=6)
        interval.pack(side="right")

        ttk.Label(frame, textvariable=self.region_var, style="Muted.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Label(frame, textvariable=self.last_time_var, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))
        self._build_preview_panel(frame)

        actions = ttk.Frame(frame, style="Card.TFrame")
        actions.pack(fill="x", pady=(16, 0))
        ttk.Button(actions, text="登录", command=self.login, style="Accent.TButton").pack(side="left", expand=True, fill="x", padx=(0, 6))
        ttk.Button(actions, text="框选区域", command=self.select_region).pack(side="left", expand=True, fill="x", padx=(6, 0))

        run_actions = ttk.Frame(frame, style="Card.TFrame")
        run_actions.pack(fill="x", pady=(10, 0))
        self.start_button = ttk.Button(run_actions, text="开始检测", command=self.start_detection)
        self.start_button.pack(side="left", expand=True, fill="x", padx=(0, 6))
        self.stop_button = ttk.Button(run_actions, text="停止", command=self.stop_detection, state="disabled")
        self.stop_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

        ttk.Button(frame, text="置顶开关", command=self.toggle_topmost).pack(fill="x", pady=(10, 0))

    def _build_preview_panel(self, parent: ttk.Frame) -> None:
        preview = ttk.Frame(parent, style="Card.TFrame")
        preview.pack(fill="x", pady=(12, 0))
        ttk.Label(preview, text="最近送检截图", style="Muted.TLabel").pack(anchor="w")
        self.preview_canvas = tk.Canvas(
            preview,
            width=292,
            height=164,
            bg="#f8fafc",
            highlightthickness=1,
            highlightbackground="#d9e2ef",
        )
        self.preview_canvas.pack(fill="x", pady=(4, 4))
        self.preview_canvas.create_text(
            146,
            82,
            text="开始检测后显示实际截帧",
            fill="#647084",
            font=("Microsoft YaHei", 9),
        )
        ttk.Label(preview, textvariable=self.preview_time_var, style="Muted.TLabel").pack(anchor="w")

    def _add_entry(self, parent: ttk.Frame, label_text: str, variable: tk.StringVar, show: str | None) -> None:
        ttk.Label(parent, text=label_text, style="Muted.TLabel").pack(anchor="w", pady=(8, 2))
        entry = ttk.Entry(parent, textvariable=variable, show=show)
        entry.pack(fill="x")

    def login(self) -> None:
        self.api_client.set_api_base_url(self.api_var.get().strip())
        self._set_status("正在登录...")

        def task() -> None:
            try:
                self.api_client.login(self.username_var.get().strip(), self.password_var.get())
                self._schedule(lambda: self._set_status("已登录，选择视频区域后开始检测。"))
            except Exception as exc:
                self._schedule(lambda: self._show_error("登录失败", exc))

        threading.Thread(target=task, daemon=True).start()

    def select_region(self) -> None:
        selector = RegionSelector(self.root)
        region = selector.select()
        if region is None:
            self._set_status("已取消区域选择。")
            return
        if not region.is_valid():
            messagebox.showwarning("区域过小", "请选择至少 80x80 的视频区域。")
            return
        self.region = region
        self.region_var.set(f"区域：{region.left},{region.top}  {region.width}x{region.height}")
        self._set_status("区域已选择，可以开始检测。")

    def start_detection(self) -> None:
        if not self.api_client.token:
            messagebox.showinfo("需要登录", "请先登录后端服务。")
            return
        if self.region is None:
            messagebox.showinfo("需要选择区域", "请先框选视频画面区域。")
            return
        if self.worker and self.worker.is_alive():
            return

        self.stop_event.clear()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self._set_status("检测运行中。")
        self.worker = threading.Thread(target=self._detection_loop, daemon=True)
        self.worker.start()

    def stop_detection(self) -> None:
        self.stop_event.set()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self._set_status("已停止检测。")

    def toggle_topmost(self) -> None:
        current = bool(self.root.attributes("-topmost"))
        self.root.attributes("-topmost", not current)
        self._set_status("窗口已置顶。" if not current else "窗口已取消置顶。")

    def _detection_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                self._schedule(lambda: self._set_status("正在截帧并检测..."))
                frame_bytes, preview_image = self._capture_region()
                self._schedule(lambda preview_image=preview_image: self._update_capture_preview(preview_image))
                model_id = self.model_id_var.get().strip() or None
                result = self.api_client.detect_frame(frame_bytes, model_id=model_id)
                self._schedule(lambda result=result: self._apply_detection_result(result))
            except Exception as exc:
                self._schedule(lambda exc=exc: self._show_error("检测失败", exc, modal=False))
            interval = max(1.0, float(self.interval_var.get() or 2.0))
            self.stop_event.wait(interval)

        self._schedule(self.stop_detection)

    def _capture_region(self) -> tuple[bytes, Image.Image]:
        if self.region is None:
            raise RuntimeError("未选择屏幕区域。")
        try:
            image = ImageGrab.grab(bbox=self.region.as_bbox(), all_screens=True).convert("RGB")
        except TypeError:
            image = ImageGrab.grab(bbox=self.region.as_bbox()).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        return buffer.getvalue(), image.copy()

    def _update_capture_preview(self, image: Image.Image) -> None:
        if self.preview_canvas is None:
            return

        preview = image.copy()
        preview.thumbnail((292, 164), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(preview)

        canvas_width = int(self.preview_canvas.cget("width"))
        canvas_height = int(self.preview_canvas.cget("height"))
        x = (canvas_width - preview.width) // 2
        y = (canvas_height - preview.height) // 2

        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_photo)
        self.preview_time_var.set(
            f"最近截帧：{datetime.now().strftime('%H:%M:%S')}  原始尺寸 {image.width}x{image.height}"
        )

    def _apply_detection_result(self, result: dict[str, Any]) -> None:
        probability = result.get("fake_probability")
        risk_level = str(result.get("risk_level") or "").lower()
        risk_text, status_key = self._risk_text_and_status(risk_level, probability)

        high_flag = status_key == "high"
        self.recent_high_flags.append(high_flag)
        sustained = len(self.recent_high_flags) == self.recent_high_flags.maxlen and sum(self.recent_high_flags) >= 3
        if sustained:
            risk_text = f"{risk_text}（连续预警）"

        self.risk_var.set(risk_text)
        self.probability_var.set(f"伪造概率：{self._format_probability(probability)}")
        self.last_time_var.set(f"最近检测：{datetime.now().strftime('%H:%M:%S')}")
        face_detected = result.get("face_detected")
        face_note = "已检测到人脸" if face_detected else "未稳定检测到人脸，结果仅供参考"
        self._set_status(face_note)
        self._apply_status(status_key)

    def _risk_text_and_status(self, risk_level: str, probability: Any) -> tuple[str, str]:
        if risk_level in {"high", "高风险"} or self._as_float(probability) >= 0.7:
            return "高风险", "high"
        if risk_level in {"medium", "middle", "中风险"} or self._as_float(probability) >= 0.4:
            return "中风险", "medium"
        if risk_level in {"low", "低风险"} or probability is not None:
            return "低风险", "low"
        return "未检测", "idle"

    def _apply_status(self, status_key: str) -> None:
        color = {
            "idle": "#172033",
            "low": "#047857",
            "medium": "#b45f06",
            "high": "#b42318",
        }.get(status_key, "#172033")
        self.risk_label.configure(foreground=color)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _show_error(self, title: str, exc: Exception, modal: bool = True) -> None:
        self._set_status(str(exc))
        self._apply_status("medium")
        if modal:
            messagebox.showerror(title, str(exc))

    def _schedule(self, callback) -> None:
        self.root.after(0, callback)

    @staticmethod
    def _as_float(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _format_probability(value: Any) -> str:
        try:
            return f"{float(value) * 100:.1f}%"
        except (TypeError, ValueError):
            return "--"


def main() -> None:
    enable_windows_dpi_awareness()
    root = tk.Tk()
    app = FloatingAssistantApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_detection(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()

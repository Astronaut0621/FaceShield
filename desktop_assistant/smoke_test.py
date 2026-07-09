"""Smoke test for the FaceShield desktop assistant API client.

This test uses a local mock HTTP server, so it does not require the real
backend, a GUI session, or screen capture permission.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from floating_assistant import FaceShieldApiClient


class MockBackendHandler(BaseHTTPRequestHandler):
    token = "smoke-token"

    def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        if self.path == "/api/auth/login":
            payload = json.loads(body.decode("utf-8"))
            if payload != {"username": "demo", "password": "demo123456"}:
                self._json({"code": 400, "message": "bad credentials", "data": None})
                return
            self._json(
                {
                    "code": 200,
                    "message": "ok",
                    "data": {"access_token": self.token, "token_type": "bearer"},
                }
            )
            return

        if self.path == "/api/detection/upload-and-detect":
            auth = self.headers.get("Authorization")
            if auth != f"Bearer {self.token}":
                self._json({"code": 401, "message": "missing token", "data": None})
                return
            if b'name="file"' not in body or b"fake-jpeg-bytes" not in body:
                self._json({"code": 400, "message": "missing multipart file", "data": None})
                return
            self._json(
                {
                    "code": 200,
                    "message": "Detection completed.",
                    "data": {
                        "task_id": 1,
                        "fake_probability": 0.82,
                        "risk_level": "high",
                        "face_detected": True,
                    },
                }
            )
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args) -> None:
        return

    def _json(self, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def main() -> None:
    server = HTTPServer(("127.0.0.1", 0), MockBackendHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        client = FaceShieldApiClient(f"http://127.0.0.1:{server.server_port}/api")
        client.login("demo", "demo123456")
        result = client.detect_frame(b"fake-jpeg-bytes")
        assert result["risk_level"] == "high"
        assert result["fake_probability"] == 0.82
        assert result["face_detected"] is True
    finally:
        server.shutdown()
        thread.join(timeout=2)

    print("desktop-assistant-smoke-ok")


if __name__ == "__main__":
    main()

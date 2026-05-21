"""Camera capture + per-frame gesture detection.

Owns the cv2 device lifecycle so the game engine never touches OpenCV
directly. Behaviour is identical to the old SmartRPSGame._init_camera /
._read_camera methods it replaces.
"""
from __future__ import annotations

import cv2

from .hand_gestures import detect_gesture


class CameraFeed:
    """Webcam wrapper. Status mirrors the old cam_status state machine:
    DEMO | REQUESTING | LIVE | DENIED | UNSUPPORTED.
    """

    def __init__(self) -> None:
        self.camera = None
        self.status: str = "DEMO"
        self.ok: bool = False
        self._open()

    def _open(self) -> None:
        try:
            self.status = "REQUESTING"
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                ok, _ = cap.read()
                if ok:
                    self.camera = cap
                    self.status = "LIVE"
                    self.ok = True
                else:
                    cap.release()
                    self.status = "DENIED"
            else:
                self.status = "UNSUPPORTED"
        except Exception:
            self.status = "UNSUPPORTED"

    def read(self):
        """Return (annotated_frame, gesture_name). Never raises."""
        if not self.ok or self.camera is None:
            return None, "No hand"
        try:
            ok, frame = self.camera.read()
            if not ok:
                return None, "No hand"
            gesture_name, processed_frame = detect_gesture(frame)
            return processed_frame, gesture_name
        except Exception:
            return None, "No hand"

    def is_open(self) -> bool:
        return bool(self.camera is not None and self.camera.isOpened())

    def release(self) -> None:
        if self.camera is not None:
            self.camera.release()

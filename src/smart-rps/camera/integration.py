from __future__ import annotations

from camera.camera import Camera
from camera.hand_gestures import detect_gesture


class CameraFeed:
    """Webcam wrapper with gesture detection. Status mirrors the old cam_status 
    state machine: DEMO | REQUESTING | LIVE | DENIED | UNSUPPORTED.
    """

    def __init__(self) -> None:
        self.camera: Camera | None = None
        self.status: str = "DEMO"
        self.ok: bool = False
        self._open()

    def _open(self) -> None:
        """Initialize camera and set initial status."""
        try:
            self.status = "REQUESTING"
            # Use Camera class from camera.py
            camera = Camera(device_index=0, width=640, height=480)
            if camera.cap.isOpened():
                # Test that we can read a frame
                test_frame = camera.read_frame()
                if test_frame is not None:
                    self.camera = camera
                    self.status = "LIVE"
                    self.ok = True
                else:
                    camera.release()
                    self.status = "DENIED"
            else:
                camera.release()
                self.status = "UNSUPPORTED"
        except Exception:
            self.status = "UNSUPPORTED"

    def read(self):
        """Return (annotated_frame, gesture_name). Never raises."""
        if not self.ok or self.camera is None:
            return None, "No hand"
        try:
            frame = self.camera.read_frame()
            if frame is None:
                return None, "No hand"
            gesture_name, processed_frame = detect_gesture(frame)
            return processed_frame, gesture_name
        except Exception:
            return None, "No hand"

    def is_open(self) -> bool:
        return bool(self.camera is not None and self.camera.cap.isOpened())

    def release(self) -> None:
        if self.camera is not None:
            self.camera.release()

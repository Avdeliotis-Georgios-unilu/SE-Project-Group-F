"""
Hand gesture detection for Rock-Paper-Scissors.

Tries the MediaPipe Tasks API first (newer mediapipe >= 0.10.30).
Falls back to a simple OpenCV contour-based heuristic if MediaPipe is
unavailable or fails to initialise.

Returns the same (gesture_name, annotated_image) tuple regardless of
which backend is active so callers don't need to care.
"""

from __future__ import annotations

import os
import cv2
import numpy as np


_USE_MEDIAPIPE = False
_hand_landmarker = None

_CAM_W, _CAM_H = 640, 480   # camera capture resolution (set in integration.py)
_ROI_SIDE = 300              # square side in camera pixels
_ROI_X1 = _CAM_W // 2 - _ROI_SIDE // 2   # 170
_ROI_Y1 = _CAM_H // 2 - _ROI_SIDE // 2   # 90
_ROI_X2 = _ROI_X1 + _ROI_SIDE             # 470
_ROI_Y2 = _ROI_Y1 + _ROI_SIDE             # 390

# Normalised fractions — import these in screens.py for the pygame overlay
ROI_NX1: float = _ROI_X1 / _CAM_W   # ≈ 0.266
ROI_NY1: float = _ROI_Y1 / _CAM_H   # = 0.1875
ROI_NX2: float = _ROI_X2 / _CAM_W   # ≈ 0.734
ROI_NY2: float = _ROI_Y2 / _CAM_H   # = 0.8125


def _init_mediapipe() -> bool:
    """One-shot MediaPipe initialisation. Returns True on success."""
    global _USE_MEDIAPIPE, _hand_landmarker

    if _USE_MEDIAPIPE and _hand_landmarker is not None:
        return True

    try:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision as mp_vision

        # MediaPipe bundles a hand landmarker model; look for it in the
        # package install path first, then in a few common places
        model_candidates = []
        try:
            import mediapipe.tasks.vision as _mv
            pkg_dir = os.path.dirname(_mv.__file__)
            bundled = os.path.join(pkg_dir, "hand_landmarker.task")
            if os.path.exists(bundled):
                model_candidates.append(bundled)
        except Exception:
            pass

        # Also check pip install location
        import site
        for sp in site.getsitepackages():
            cand = os.path.join(sp, "mediapipe", "tasks", "vision",
                                "hand_landmarker.task")
            if os.path.exists(cand):
                model_candidates.append(cand)

        if not model_candidates:
            # Download the model if not found
            import urllib.request
            model_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(model_dir, exist_ok=True)
            model_path = os.path.join(model_dir, "hand_landmarker.task")
            if not os.path.exists(model_path):
                url = ("https://storage.googleapis.com/mediapipe-models/"
                       "hand_landmarker/hand_landmarker/float16/latest/"
                       "hand_landmarker.task")
                try:
                    urllib.request.urlretrieve(url, model_path)
                    model_candidates.append(model_path)
                except Exception:
                    print("[hand_gestures] Could not download MediaPipe model.")
                    return False
            else:
                model_candidates.append(model_path)

        model_path = model_candidates[0]

        base_options = mp_tasks.BaseOptions(model_asset_path=model_path)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            running_mode=mp_vision.RunningMode.IMAGE,
        )
        _hand_landmarker = mp_vision.HandLandmarker.create_from_options(options)
        _USE_MEDIAPIPE = True
        print("[hand_gestures] MediaPipe HandLandmarker initialised.")
        return True

    except Exception as exc:
        print(f"[hand_gestures] MediaPipe init failed: {exc}")
        return False


def _mediapipe_detect(frame: np.ndarray) -> tuple[str, np.ndarray]:
    
    import mediapipe as mp

    image = cv2.flip(frame, 1)
    ih, iw = image.shape[:2]

    sx1 = max(0, min(_ROI_X1, iw - 1))
    sy1 = max(0, min(_ROI_Y1, ih - 1))
    sx2 = max(sx1 + 1, min(_ROI_X2, iw))
    sy2 = max(sy1 + 1, min(_ROI_Y2, ih))

    roi_crop = image[sy1:sy2, sx1:sx2]
    rh, rw = roi_crop.shape[:2]
    rgb_crop = cv2.cvtColor(roi_crop, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_crop)
    result = _hand_landmarker.detect(mp_image)

    gesture_name = "No hand"

    if result.hand_landmarks:
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (0, 9), (9, 10), (10, 11), (11, 12),
            (0, 13), (13, 14), (14, 15), (15, 16),
            (0, 17), (17, 18), (18, 19), (19, 20),
            (5, 9), (9, 13), (13, 17),
        ]
        for landmarks in result.hand_landmarks:
            # Remap landmark coords from crop space -> full frame space
            def _fpt(lm):
                return (sx1 + int(lm.x * rw), sy1 + int(lm.y * rh))

            for lm in landmarks:
                cv2.circle(image, _fpt(lm), 3, (61, 255, 142), -1)
            for c in connections:
                cv2.line(image, _fpt(landmarks[c[0]]), _fpt(landmarks[c[1]]),
                         (61, 255, 142), 1)

            # gesture classification (finger-tip vs PIP joint y-position)
            index_up  = landmarks[8].y  < landmarks[6].y
            middle_up = landmarks[12].y < landmarks[10].y
            ring_up   = landmarks[16].y < landmarks[14].y
            pinky_up  = landmarks[20].y < landmarks[18].y
            fingers_up = sum([index_up, middle_up, ring_up, pinky_up])

            if fingers_up == 0:
                gesture_name = "Rock"
            elif fingers_up == 4:
                gesture_name = "Paper"
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture_name = "Scissors"
            else:
                gesture_name = "Unknown"
            break  # only first hand

    return gesture_name, image



def _opencv_detect(frame: np.ndarray) -> tuple[str, np.ndarray]:
    image = cv2.flip(frame, 1)
    ih, iw = image.shape[:2]

    sx1 = max(0, min(_ROI_X1, iw - 1))
    sy1 = max(0, min(_ROI_Y1, ih - 1))
    sx2 = max(sx1 + 1, min(_ROI_X2, iw))
    sy2 = max(sy1 + 1, min(_ROI_Y2, ih))

    # Crop to ROI for detection
    roi = image[sy1:sy2, sx1:sx2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Skin colour range (broad)
    lower = np.array([0, 20, 70], dtype=np.uint8)
    upper = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    gesture_name = "No hand"

    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area > 3000:  # Minimum hand size
            
            hull = cv2.convexHull(largest, returnPoints=False)
            if len(hull) > 3:
                try:
                    defects = cv2.convexityDefects(largest, hull)
                except Exception:
                    defects = None

                finger_count = 0
                if defects is not None and len(defects) > 0:
                    for i in range(defects.shape[0]):
                        s, e, f, d = defects[i, 0]
                        if d > 8000:  # Deep enough defect = finger gap
                            finger_count += 1
                    finger_count += 1  # Compensate

                # Simple heuristic
                hull_area = cv2.contourArea(cv2.convexHull(largest))
                solidity = area / hull_area if hull_area > 0 else 0

                # Draw largest contour
                cv2.drawContours(roi, [largest], -1, (0, 255, 0), 2)

                if solidity > 0.85:
                    gesture_name = "Rock"
                elif finger_count >= 3:
                    gesture_name = "Paper"
                elif 1 <= finger_count <= 2:
                    gesture_name = "Scissors"

    return gesture_name, image


_INIT_ATTEMPTED = False


def detect_gesture(frame: np.ndarray) -> tuple[str, np.ndarray]:

   # Detect a Rock / Paper / Scissors gesture 
    global _INIT_ATTEMPTED, _USE_MEDIAPIPE

    if not _INIT_ATTEMPTED:
        _INIT_ATTEMPTED = True
        _USE_MEDIAPIPE = _init_mediapipe()

    if _USE_MEDIAPIPE:
        try:
            return _mediapipe_detect(frame)
        except Exception as exc:
            print(f"[hand_gestures] MediaPipe runtime error: {exc}")
            _USE_MEDIAPIPE = False

    return _opencv_detect(frame)

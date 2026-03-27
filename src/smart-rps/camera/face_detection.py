import cv2

try:
    from .camera import get_camera
except ImportError:
    from camera import get_camera


def _smooth_box(previous_box, current_box, alpha=0.25, deadzone_px=3):
    if previous_box is None:
        return current_box

    smoothed = []
    for old_v, new_v in zip(previous_box, current_box):
        value = int((1.0 - alpha) * old_v + alpha * new_v)
        # Ignore tiny coordinate changes that cause visible box jitter.
        if abs(value - old_v) < deadzone_px:
            value = old_v
        smoothed.append(value)
    return tuple(smoothed)


def run_face_detection(device_index=0, box_padding=0.25):
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    if face_cascade.empty():
        print("[ERROR] Could not load Haar cascade for face detection.")
        return

    cam = get_camera(device_index=device_index, width=640, height=480)
    if cam is None:
        print("[ERROR] Camera could not be opened.")
        return

    smoothed_box = None

    try:
        while True:
            frame = cam.read_frame()
            if frame is None:
                print("[WARN] Could not read frame from camera.")
                break

            frame = cv2.resize(frame, (640, 480))
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=6,
                minSize=(60, 60),
            )

            frame_h, frame_w = frame.shape[:2]
            if len(faces) > 0:
                # Use the largest face for more stable single-person tracking.
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                pad_w = int(w * box_padding)
                pad_h = int(h * box_padding)

                x1 = max(0, x - pad_w)
                y1 = max(0, y - pad_h)
                x2 = min(frame_w, x + w + pad_w)
                y2 = min(frame_h, y + h + pad_h)

                smoothed_box = _smooth_box(smoothed_box, (x1, y1, x2, y2), alpha=0.25, deadzone_px=3)
            else:
                smoothed_box = None

            if smoothed_box is not None:
                x1, y1, x2, y2 = smoothed_box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_face_detection(box_padding=0.35)
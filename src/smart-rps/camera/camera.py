import cv2

class Camera:
    def __init__(self, device_index=0, width=640, height=480):
        self.cap = cv2.VideoCapture(device_index)  # 0 = first USB cam
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

    def read_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        self.cap.release()

# Manual fallback if no camera is detected
def get_camera(device_index=0, width=640, height=480):
    cam = Camera(device_index=device_index, width=width, height=height)
    if cam.cap.isOpened():
        return cam
    print("[WARN] No camera found — switching to manual input mode")
    cam.release()
    return None 
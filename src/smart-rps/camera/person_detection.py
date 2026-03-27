import cv2, numpy as np

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cam = cv2.VideoCapture(0)
while True:
    ret, frame = cam.read()
    frame = cv2.resize(frame, (640, 480))
    boxes, _ = hog.detectMultiScale(frame, winStride=(8, 8))
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("Person Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cam.release()
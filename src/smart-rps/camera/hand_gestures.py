import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils  #draws the hand

hand_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def detect_gesture(frame):
    image = cv2.flip(frame, 1) #flips the cam so it s mirrored
    image_height, image_width, _ = image.shape

    square_size = 300                             #creates the square for the hand
    square_x1 = image_width // 2 - square_size // 2
    square_y1 = image_height // 2 - square_size // 2    #placement of the square so it s in the middle
    square_x2 = square_x1 + square_size
    square_y2 = square_y1 + square_size

    cv2.rectangle(image, (square_x1, square_y1), (square_x2, square_y2), (0, 255, 0), 2) # draws the square

    hand_area = image[square_y1:square_y2, square_x1:square_x2]  #only analyzes what's inside the square
    hand_area_rgb = cv2.cvtColor(hand_area, cv2.COLOR_BGR2RGB) #converts bgr to rgb bc open cv uses bgr, mp expects rgb

    result = hand_detector.process(hand_area_rgb) #analyzes if there is a hand

    gesture_name = "No hand"

    if result.multi_hand_landmarks:
        for one_hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(hand_area, one_hand, mp_hands.HAND_CONNECTIONS) #draws if hand in box

            points = one_hand.landmark

            index_up = points[8].y < points[6].y     #checks finger positions
            middle_up = points[12].y < points[10].y
            ring_up = points[16].y < points[14].y
            pinky_up = points[20].y < points[18].y

            if not index_up and not middle_up and not ring_up and not pinky_up:
                gesture_name = "Rock"
            elif index_up and middle_up and ring_up and pinky_up:
                gesture_name = "Paper"
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture_name = "Scissors"
            else:
                gesture_name = "Unknown"

    return gesture_name, image
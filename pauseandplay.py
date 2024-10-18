import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Open webcam feed
cap = cv2.VideoCapture(0)

# Variables to control action timing
last_gesture_time = time.time()
gesture_cooldown = 2  # Cooldown time in seconds to avoid multiple triggers

# Function to detect open or closed palm gestures
def detect_open_or_closed_palm(landmarks):
    # Get y-coordinate of key finger landmarks relative to palm base
    thumb_tip_y = landmarks[mp_hands.HandLandmark.THUMB_TIP].y
    index_tip_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
    middle_tip_y = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
    ring_tip_y = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y
    pinky_tip_y = landmarks[mp_hands.HandLandmark.PINKY_TIP].y
    palm_base_y = landmarks[mp_hands.HandLandmark.WRIST].y

    # Open palm: all fingertips should be above the palm base
    if (thumb_tip_y < palm_base_y and index_tip_y < palm_base_y and middle_tip_y < palm_base_y
        and ring_tip_y < palm_base_y and pinky_tip_y < palm_base_y):
        return "open_palm"

    # Closed palm: most fingertips should be near or below the palm base
    if (index_tip_y > palm_base_y and middle_tip_y > palm_base_y and ring_tip_y > palm_base_y and pinky_tip_y > palm_base_y):
        return "closed_palm"

    return None

# Main loop to process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the image horizontally for a selfie-view
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (MediaPipe expects RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame and detect hand landmarks
    result = hands.process(rgb_frame)

    # Check if any hand landmarks are detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detect if hand gesture is open palm or closed palm
            gesture = detect_open_or_closed_palm(hand_landmarks.landmark)

            current_time = time.time()

            if gesture == "open_palm":
                # Trigger pause if open palm is detected (with cooldown)
                if current_time - last_gesture_time > gesture_cooldown:
                    pyautogui.press('space')  # Simulate spacebar press (Pause)
                    last_gesture_time = current_time
                    cv2.putText(frame, "Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            elif gesture == "closed_palm":
                # Trigger play if closed palm is detected (with cooldown)
                if current_time - last_gesture_time > gesture_cooldown:
                    pyautogui.press('space')  # Simulate spacebar press (Play)
                    last_gesture_time = current_time
                    cv2.putText(frame, "Play", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow("Hand Gesture - Play/Pause", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

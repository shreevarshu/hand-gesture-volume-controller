import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Initialize Audio Utilities
def get_volume_control():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    return volume

volume = get_volume_control()

def adjust_volume(change):
    """Adjusts the volume based on the change value"""
    current_volume = volume.GetMasterVolumeLevelScalar()
    new_volume = min(max(current_volume + change, 0.0), 1.0)
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    print(f"Volume set to {new_volume * 100:.0f}%")

def mute_volume():
    """Mutes the volume"""
    volume.SetMasterVolumeLevelScalar(0.0, None)
    print("Volume muted")

def unmute_volume():
    """Unmutes the volume"""
    volume.SetMasterVolumeLevelScalar(0.5, None)  # Set to 50% volume
    print("Volume unmuted")

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not found or could not be opened.")
        return

    print("Frame captured successfully")
    print("Attempting to read frame...")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Convert frame to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks and connections
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Get hand landmarks
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                    # Convert normalized coordinates to pixel coordinates
                    h, w, _ = frame.shape
                    thumb_tip_x, thumb_tip_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    index_tip_x, index_tip_y = int(index_tip.x * w), int(index_tip.y * h)
                    middle_tip_x, middle_tip_y = int(middle_tip.x * w), int(middle_tip.y * h)
                    ring_tip_x, ring_tip_y = int(ring_tip.x * w), int(ring_tip.y * h)
                    pinky_tip_x, pinky_tip_y = int(pinky_tip.x * w), int(pinky_tip.y * h)

                    # Define thresholds for palm detection
                    # Simple approach: check if the distance between fingertips is relatively large
                    # indicating an open palm
                    thumb_index_dist = ((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2) ** 0.5
                    index_middle_dist = ((index_tip_x - middle_tip_x) ** 2 + (index_tip_y - middle_tip_y) ** 2) ** 0.5
                    middle_ring_dist = ((middle_tip_x - ring_tip_x) ** 2 + (middle_tip_y - ring_tip_y) ** 2) ** 0.5
                    ring_pinky_dist = ((ring_tip_x - pinky_tip_x) ** 2 + (ring_tip_y - pinky_tip_y) ** 2) ** 0.5

                    # Threshold for detecting open palm (you might need to adjust these values)
                    open_palm_threshold = 50
                    if (thumb_index_dist > open_palm_threshold and
                        index_middle_dist > open_palm_threshold and
                        middle_ring_dist > open_palm_threshold and
                        ring_pinky_dist > open_palm_threshold):
                        mute_volume()

            cv2.imshow('Camera Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting program")
                break
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

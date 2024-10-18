import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Initialize MediaPipe Hands
mp_hands    = mp.solutions.hands
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

                    # Example gesture detection logic
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    # Convert normalized coordinates to pixel coordinates
                    h, w, _ = frame.shape
                    thumb_tip_x, thumb_tip_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    index_tip_x, index_tip_y = int(index_tip.x * w), int(index_tip.y * h)

                    # Calculate distance between thumb and index finger
                    distance = ((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2) ** 0.5

                    # Define thresholds for volume adjustment
                    min_distance = 50  # Minimum distance for the widest hand
                    max_distance = 200  # Maximum distance for the narrowest hand
                    volume_range = 0.1  # Range of volume change per distance

                    # Scale distance to volume change
                    if distance > min_distance:
                        change = min((distance - min_distance) / (max_distance - min_distance), 1.0) * volume_range
                        adjust_volume(change)  # Increase volume
                    elif distance < max_distance:
                        change = (max_distance - distance) / (max_distance - min_distance) * volume_range
                        adjust_volume(-change)  # Decrease volume

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

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
    # Set to a reasonable default volume level (e.g., 50%)
    volume.SetMasterVolumeLevelScalar(0.5, None)
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

                    # Convert normalized coordinates to pixel coordinates
                    h, w, _ = frame.shape
                    thumb_tip_x, thumb_tip_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    index_tip_x, index_tip_y = int(index_tip.x * w), int(index_tip.y * h)

                    # Calculate distances for gesture detection
                    thumb_index_distance = ((thumb_tip_x - index_tip_x) ** 2 + (thumb_tip_y - index_tip_y) ** 2) ** 0.5

                    # Gesture detection logic
                    if thumb_index_distance < 50:  # Pinch gesture
                        if thumb_tip_x < w / 2 and index_tip_x < w / 2:
                            mute_volume()
                        elif thumb_tip_x > w / 2 and index_tip_x > w / 2:
                            unmute_volume()

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

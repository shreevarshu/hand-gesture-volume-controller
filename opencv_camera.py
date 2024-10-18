import cv2

def test_camera_basic():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not found or could not be opened.")
        return

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            cv2.imshow('Camera Feed', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera_basic()

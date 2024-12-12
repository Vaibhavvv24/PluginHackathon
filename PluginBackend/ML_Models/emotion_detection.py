import cv2
from deepface import DeepFace

def detect_emotions():
    # Initialize webcam feed
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    print("Press 'q' to quit the application.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to read from the webcam.")
            break

        try:
            # Detect emotions using DeepFace
            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

            # Draw the bounding box and display emotion
            if 'region' in analysis:
                x, y, w, h = analysis['region'].values()
                dominant_emotion = analysis['dominant_emotion']

                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Display the detected emotion on the frame
                cv2.putText(
                    frame,
                    f"Detected Emotion: {dominant_emotion}",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

                # Also display near the bounding box
                cv2.putText(
                    frame,
                    f"Emotion: {dominant_emotion}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

        except Exception as e:
            print(f"Error processing frame: {e}")

        # Display the video feed with annotations
        cv2.imshow("Facial Expression Detection", frame)

        # Quit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_emotions()
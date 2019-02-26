import cv2

from src.video import compress
from src.face import FaceTracker

WINDOW_NAME = "Ubble Interview"


def run():
    # init video feed
    cv2.namedWindow(WINDOW_NAME)
    # capture the video from the webcam
    video_capture = cv2.VideoCapture(0)
    face_tracker = FaceTracker()

    while True:
        ret, frame = video_capture.read()
        frame = compress(frame, 2)  # to make it run faster

        if not ret:
            break

        feedback, output_frame = face_tracker.run(frame)
        # show frames
        cv2.imshow(WINDOW_NAME, output_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


if __name__ == "__main__":
    run()

import cv2
import numpy as np
from src.config import get_algorithm_params
import dlib

NO_FACE_IN_FRAME = "NO_FACE_IN_FRAME"
FACE_DETECTED = "FACE_DETECTED"
FACE_TRACKER = "FACE_TRACKER"


class FaceTracker:
    def __init__(self):
        self.params = get_algorithm_params(FACE_TRACKER.lower())

        # load dlib detector
        self.detector = dlib.get_frontal_face_detector()

    def run(self, frame):
        # compute the bounding box
        # this algorithm requires grayscale frames
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.compute_bounding_box(gray_frame)

    def compute_bounding_box(self, gray_frame):
        """
        computes the bounding box for an image
        (4 corners in which the face is in)
        :return:
        """

        feedback = NO_FACE_IN_FRAME

        # The second argument is the number of times we will upscale the image (in this case we don't, as
        # it increase computation time)
        # The third argument to run is an optional adjustment to the detection threshold,
        # where a negative value will return more detections and a positive value fewer.
        candidate_bounding_boxes, scores, idx = self.detector.run(gray_frame, 1, -0.3)

        if len(candidate_bounding_boxes) > 0:
            feedback = FACE_DETECTED

            # find best bounding box:
            best_bounding_box = self.find_best_bounding_box(
                candidate_bounding_boxes, scores, gray_frame
            )

        color = (0, 255, 0) if feedback == FACE_DETECTED else (0, 0, 255)
        output_frame = cv2.putText(
            cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB),
            feedback,
            (gray_frame.shape[1] // 2, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
            cv2.LINE_AA,
        )

        if feedback == FACE_DETECTED:
            output_frame = cv2.rectangle(
                output_frame,
                (best_bounding_box.left(), best_bounding_box.top()),
                (best_bounding_box.right(), best_bounding_box.bottom()),
                (0, 255, 0),
                1,
            )

        return feedback, output_frame

    def find_best_bounding_box(self, candidate_bounding_boxes, scores, gray_frame):
        # computes the size of the bounding box diagonal
        mean_sizes = (
            np.sum(
                np.array(
                    [
                        [rect.top() - rect.bottom(), rect.left() - rect.right()]
                        for rect in candidate_bounding_boxes
                    ]
                )
                ** 2,
                axis=-1,
            )
            ** 0.5
        )

        # computes the position of the middle of bounding boxes with respect to the middle of the image
        mean_points = np.array(
            [
                [(rect.top() + rect.bottom()) / 2.0, (rect.left() + rect.right()) / 2.0]
                for rect in candidate_bounding_boxes
            ]
        ) - np.array([gray_frame.shape[0] / 2.0, gray_frame.shape[1] / 2.0])

        # computes the distances to center, divided by the bounding box diagonal
        prop_dist = np.sum(mean_points ** 2, axis=-1) ** 0.5 / mean_sizes

        # gets the closer bounding box to the center
        best_bounding_box_id = np.argmin(prop_dist)

        # compute best bounding box
        best_bounding_box = dlib.rectangle(
            int(candidate_bounding_boxes[best_bounding_box_id].left()),
            int(candidate_bounding_boxes[best_bounding_box_id].top()),
            int(candidate_bounding_boxes[best_bounding_box_id].right()),
            int(candidate_bounding_boxes[best_bounding_box_id].bottom()),
        )

        return best_bounding_box

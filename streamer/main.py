import cv2
import time
import boto3

from src.video import compress
from src.face import FaceTracker

WINDOW_NAME = "Ubble Interview"


def save_frame_to_s3_bucket_with_timestamp(frame, bucket, is_output=False):
    """
    Save the frame to s3 bucket with a timestamp in the name of image.
    This will always save the image as a JPEG file.

    Parameters
    ----------
    frame: np.ndarray
        CV2 captured frame object
    bucket: str
        The name of the bucket we want to access.
    is_output: bool
        Boolean to tell if the frame is an output file or not

    Returns
    -------
    path: str
        The path of image on the S3 bucket.
    """
    # Create a name for image to be created with a timestamp in it
    if is_output:
        input_image_name = 'output_%s.jpg' % time.strftime('%Y%m%d-%H%M%S')
    else:
        input_image_name = '%s.jpg' % time.strftime('%Y%m%d-%H%M%S')

    # Convert the frame image to string. This is dirty but useful as we don't
    # need to save the image on local disk
    image_string = cv2.imencode('.jpg', frame)[1].tostring()

    # Put the image and the body of image on the designated path
    bucket.put_object(Key=input_image_name, Body=image_string)

    return image_string


def run():
    # init video feed
    cv2.namedWindow(WINDOW_NAME)
    # capture the video from the webcam
    video_capture = cv2.VideoCapture(0)
    face_tracker = FaceTracker()

    # Get the s3 resource
    s3 = boto3.resource('s3', endpoint_url='http://localhost:4572')
    # Get the bucket.
    bucket = s3.Bucket('ubblebucket')

    while True:
        # Get the coloured frame (ndarray) of the video captured
        ret, frame = video_capture.read()
        frame = compress(frame, 2)  # to make it run faster

        if not ret:
            break

        # Save the frame to S3 and get the path
        input_frame_path = save_frame_to_s3_bucket_with_timestamp(frame, bucket)

        # feedback is the status of face detected and output_frame is the grayframe with text on it
        feedback, output_frame = face_tracker.run(frame)

        # Save the output frame to S3 and get the path
        output_frame_path = save_frame_to_s3_bucket_with_timestamp(output_frame, bucket, True)

        # show frames
        cv2.imshow(WINDOW_NAME, output_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release video_capture if job is finished
    video_capture.release()


if __name__ == "__main__":
    run()

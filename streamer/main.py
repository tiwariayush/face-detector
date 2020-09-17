import cv2
import time
import boto3
import botocore
import requests
import logging

from src.video import compress
from src.face import FaceTracker

WINDOW_NAME = "Ubble Interview"
S3_BUCKET_NAME = "ubblebucket"
S3_ENDPOINT = "http://localhost:4572"
DYNAMODB_TABLE_NAME = "ubbledb"
DYNAMODB_ENDPOINT = "http://localhost:4569"

logger = logging.getLogger()


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
        image_name = 'output_%s.jpg' % time.strftime('%Y%m%d-%H%M%S')
    else:
        image_name = '%s.jpg' % time.strftime('%Y%m%d-%H%M%S')

    # Convert the frame image to string. This is dirty but useful as we don't
    # need to save the image on local disk
    image_string = cv2.imencode('.jpg', frame)[1].tostring()

    # Put the image and the body of image on the designated path
    bucket.put_object(Key=image_name, Body=image_string)

    return image_name


def run():
    # init video feed
    cv2.namedWindow(WINDOW_NAME)
    # capture the video from the webcam
    video_capture = cv2.VideoCapture(0)
    face_tracker = FaceTracker()

    # Get the s3 resource
    s3 = boto3.resource('s3', endpoint_url=S3_ENDPOINT)
    # Get the bucket.
    bucket = s3.Bucket(S3_BUCKET_NAME)

    # Get the dynamodb resource
    dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)
    # Get the table
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    # Delete old dynamoDB table if exists
    try:
        table.delete()
    except botocore.exceptions.ResourceNotFoundException:
        pass

    # Create new table
    table = dynamodb.create_table(
        TableName=DYNAMODB_TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Counter which we will use as ID
    counter = 1

    while True:
        start_time = time.time()
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

        # Add data to dynamoDB Table
        table.put_item(
            Item={
                'id': str(counter),
                'input_frame_path': input_frame_path,
                'output_frame_path': output_frame_path,
                'feedback': feedback
            }
        )
        # Increase the counter
        counter += 1

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    stop_time = time.time()
    # Release video_capture if job/streaming is finished
    video_capture.release()

    # Since for every single stream we have a new table, hence all the data in the table
    # is required to be saved in postgres. In this case, we can use `scan` as we don't
    # remove or filter anything from results.
    table_data = table.scan()

    # Send API request to save the data in Postgres
    # Send POST request to API to create StreamerSession object
    session_data = {
        'start_time': start_time,
        'stop_time': stop_time,
    }
    response = requests.post(
        'http://localhost:8000/api/stream-sessions/',
        data=session_data
    )

    # Get the stream session ID if we have successful response
    if response.status_code == 201:
        session_id = response.json()['id']
        logger.info(f'Stream session with ID {session_id} created')
        # Create new Stream Iteration objects for every iterations using POST request
        for item in table_data['Items']:
            data = {
                'session': session_id,
                'feedback': item['feedback'],
                'input_frame_url': f"{S3_ENDPOINT}/{S3_BUCKET_NAME}/{item['input_frame_path']}",
                'output_frame_url': f"{S3_ENDPOINT}/{S3_BUCKET_NAME}/{item['output_frame_path']}"
            }
            requests.post('http://localhost:8000/api/stream-iterations/', data=data)


if __name__ == "__main__":
    run()

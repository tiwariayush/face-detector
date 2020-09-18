from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from .models import StreamerSession, SingleStreamIteration
from .serializers import StreamerSessionSerializer, StreamIterationSerializer
from .constants import FACE_DETECTED

# initialize the APIClient app
client = APIClient()


class StreamingSessionTest(TestCase):
    """
    Test module to check stream session links all streaming session
    """
    def setUp(self):
        self.session_1 = StreamerSession.objects.create(id=1)
        self.session_2 = StreamerSession.objects.create(id=2)
        self.session_3 = StreamerSession.objects.create(id=3)

    def test_get_all_streamer_sessions(self):
        # get API response
        response = client.get("/api/stream-sessions/")
        streamer_sessions = StreamerSession.objects.all()
        serializer = StreamerSessionSerializer(streamer_sessions, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_streaming_session(self):
        response = client.get('/api/stream-sessions/1/')
        streamer_session = StreamerSession.objects.get(id=1)
        serializer = StreamerSessionSerializer(streamer_session)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class SingleStreamIterationTest(TestCase):
    """
    Test module to test single stream iteration link
    """
    def setUp(self):
        # create sessions
        self.session_1 = StreamerSession.objects.create(id=1)
        self.session_2 = StreamerSession.objects.create(id=2)
        # create iterations for sessions
        self.iteration_1 = SingleStreamIteration.objects.create(
            id=1,
            feedback=FACE_DETECTED,
            input_frame_url='https://xyz.com/test.jpg',
            output_frame_url='https://xyz.com/testoutput1.jpg',
            detected_face_url='https://xyz.com/testdetected1.jpg',
            session=self.session_1
        )
        self.iteration_2 = SingleStreamIteration.objects.create(
            id=2,
            feedback=FACE_DETECTED,
            input_frame_url='https://xyz.com/test.jpg',
            output_frame_url='https://xyz.com/testoutput2.jpg',
            detected_face_url='https://xyz.com/testdetected2.jpg',
            session=self.session_1
        )
        self.iteration_3 = SingleStreamIteration.objects.create(
            id=3,
            feedback=FACE_DETECTED,
            input_frame_url='https://xyz.com/test.jpg',
            output_frame_url='https://xyz.com/testoutput3.jpg',
            detected_face_url='https://xyz.com/testdetected3.jpg',
            session=self.session_2
        )
        self.iteration_4 = SingleStreamIteration.objects.create(
            id=4,
            session=self.session_2
        )

    def test_get_all_iterations(self):
        # get API response
        response = client.get("/api/stream-iterations/")
        stream_iterations = SingleStreamIteration.objects.all()
        serializer = StreamIterationSerializer(stream_iterations, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_single_stream_iteration(self):
        response = client.get('/api/stream-iterations/1/')
        stream_iteration = SingleStreamIteration.objects.get(id=1)
        serializer = StreamIterationSerializer(stream_iteration)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_extracted_faces_for_session_if_all_face_detected(self):
        response = client.get('/api/stream-sessions/1/faces')
        data = {
            'session_id': 1,
            'extracted_faces_links': [
                'https://xyz.com/testdetected2.jpg',
                'https://xyz.com/testdetected1.jpg',
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

    def test_get_extracted_faces_for_session_if_some_face_detected(self):
        response = client.get('/api/stream-sessions/2/faces')
        data = {
            'session_id': 2,
            'extracted_faces_links': [
                'https://xyz.com/testdetected3.jpg',
            ]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, data)

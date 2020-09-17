from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .serializers import StreamerSessionSerializer, StreamIterationSerializer
from .models import StreamerSession, SingleStreamIteration
from . import constants


class StreamerSessionViewSet(viewsets.ModelViewSet):
    """
    List all stream sessions
    """
    queryset = StreamerSession.objects.all().order_by('start_time')
    serializer_class = StreamerSessionSerializer


class SingleStreamIterationViewSet(viewsets.ModelViewSet):

    queryset = SingleStreamIteration.objects.all()
    serializer_class = StreamIterationSerializer


@api_view(['GET'])
def get_extracted_faces(request, stream_session_id):
    """
    Returns the faces extracted for the stream session.

    :parameter
    request: API Request
    stream_session_id: ID of the stream session for which we want the extracted faces

    :return:
    Returns the links of the images of extracted faces hosted on S3.
    """
    # We fetch the requested Streaming session
    stream_session = get_object_or_404(StreamerSession, id=stream_session_id)

    # We can now start building the response data.
    stream_iterations = stream_session.stream_iterations

    # Get all the output frame from the stream iterations
    faces_data = {
        'session_id': stream_session_id,
        'extracted_faces_links': [],
    }

    for single_stream_iteration in stream_iterations.all():
        if single_stream_iteration.feedback == constants.FACE_DETECTED:
            faces_data['extracted_faces_links'].append(single_stream_iteration.output_frame_url)

    return Response(faces_data)

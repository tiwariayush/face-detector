from rest_framework import serializers

from .models import StreamerSession, SingleStreamIteration


class StreamerSessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StreamerSession
        fields = ('start_time', 'stop_time', 'stream_iterations')


class StreamIterationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SingleStreamIteration
        fields = (
            'unique_token',
            'input_frame_url',
            'output_frame_url',
            'feedback',
        )

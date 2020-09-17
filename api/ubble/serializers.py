from rest_framework import serializers

from .models import StreamerSession, SingleStreamIteration


class StreamerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamerSession
        fields = "__all__"


class StreamIterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleStreamIteration
        fields = "__all__"

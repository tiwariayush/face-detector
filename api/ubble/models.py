import uuid
from django.db import models
from django.utils import timezone

from . import constants


class StreamerSession(models.Model):
    """
    A Session for each streaming period.

    Attributes
    ----------
    start_time: datetime
        Time when the session was started
    stop_time: datetime
        Time when the session finished
    """
    id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField(
        "Start time",
        editable=False,
        default=timezone.now,
        help_text="When this stream was started.",
    )
    stop_time = models.DateTimeField(
        "Stop time",
        editable=False,
        default=timezone.now,
        help_text="When this stream stopped.",
    )

    def __str__(self):
        return f"Session #{self.id}"


class SingleStreamIteration(models.Model):
    """
    Single iteration of each stream session.

    Attributes
    ----------
    unique_token: UUID
        Unique token ID for each iteration.
        This is helpful to sometime differentiate between the iterations with similar
        frames as we are not using timestamp for iteration to not make things slow for
        streamer.
    feedback: Text
        Status of the frame
    session: Foreign Key
        Parent session related to this iteration
    input_frame_url: URL
        S3 URL for input frame
    output_frame_url: URL
        S3 URL for output frame
    detected_face_url: URL
        S3 URL for extracted face
    """
    id = models.AutoField(primary_key=True)
    unique_token = models.UUIDField(default=uuid.uuid4, unique=True)
    feedback = models.TextField(
        'Feedback', choices=constants.FEEDBACK_CHOICES,
        default=constants.NO_FACE_IN_FRAME,
    )
    session = models.ForeignKey(
        'StreamerSession',
        related_name='stream_iterations',
        verbose_name="Streamer Session",
        # Delete the frames related if the stream session is deleted
        on_delete=models.CASCADE,
    )
    input_frame_url = models.URLField(verbose_name="Input frame image URL")
    output_frame_url = models.URLField(verbose_name="Output frame image URL")
    detected_face_url = models.URLField(verbose_name="Detected face image URL")

    def __str__(self):
        return f'Iteration with UUID {str(self.unique_token)} for {str(self.session)}'

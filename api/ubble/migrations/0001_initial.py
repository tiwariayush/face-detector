# Generated by Django 2.1.7 on 2020-09-17 11:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SingleStreamIteration',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('unique_token', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('feedback', models.TextField(choices=[('NO_FACE_IN_FRAME', 'no face in frame'), ('FACE_DETECTED', 'face detected')], default='NO_FACE_IN_FRAME', verbose_name='Feedback')),
                ('input_frame_url', models.URLField(verbose_name='Input frame image URL')),
                ('output_frame_url', models.URLField(verbose_name='Input frame image URL')),
            ],
        ),
        migrations.CreateModel(
            name='StreamerSession',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='When this stream was started.', verbose_name='Start time')),
                ('stop_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, help_text='When this stream stopped.', verbose_name='Stop time')),
            ],
        ),
        migrations.AddField(
            model_name='singlestreamiteration',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frames', to='ubble.StreamerSession', verbose_name='Streamer Session'),
        ),
    ]

from django.contrib import admin

from .models import StreamerSession, SingleStreamIteration

# Register the models for admin
admin.site.register(StreamerSession)
admin.site.register(SingleStreamIteration)

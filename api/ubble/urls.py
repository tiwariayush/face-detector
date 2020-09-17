from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'stream-sessions', views.StreamerSessionViewSet)
router.register(r'stream-iterations', views.SingleStreamIterationViewSet)

urlpatterns = [
    # Include the ViewSet url (these are mostly self generated ans less explicit, but
    # gives us urls to traverse through data.
    path('', include(router.urls)),

    # Extracted faced for the stream session URLS
    path(
        'stream-sessions/<int:stream_session_id>/faces',
        views.get_extracted_faces,
        name='get_extracted_faces',
    ),
]

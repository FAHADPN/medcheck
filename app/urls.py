from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recordingViewSet, recording

router = DefaultRouter()
router.register(r"recording", recordingViewSet)

urlpatterns = [
    path("recording/", recording.as_view(), name="recording"),
    path("", include(router.urls)),
]
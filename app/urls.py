from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recordingViewSet, recording, ivr_conversation

router = DefaultRouter()
router.register(r"recording", recordingViewSet)

urlpatterns = [
    path("recording/", recording, name="recording"),
    path('conversation/<str:session_id>/', ivr_conversation, name='ivr_conversation'),
    path("", include(router.urls)),
]
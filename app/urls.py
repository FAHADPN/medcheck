from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recordingViewSet

router = DefaultRouter()
router.register(r"recording", recordingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
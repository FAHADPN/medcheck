from rest_framework import serializers
from .serializers import recordingSerializer
from .models import recording
from rest_framework import viewsets

class recordingViewSet(viewsets.ModelViewSet):
    queryset = recording.objects.all()
    serializer_class = recordingSerializer
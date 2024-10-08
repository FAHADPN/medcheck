from rest_framework import serializers
from .serializers import recordingSerializer
from .models import recording
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ehr.models import Patient

class recordingViewSet(viewsets.ModelViewSet):
    queryset = recording.objects.all()
    serializer_class = recordingSerializer

api_view(['POST'])
def recording(request):
    data = request.data
    patient = Patient.objects.get(id=1)
    recording.objects.create(patient=patient, recording=data['recording'])
    return Response({'status': 'recording created'})

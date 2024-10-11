from django.shortcuts import render
from rest_framework import viewsets
from .models import Patient
from .serializers import PatientSerializer
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
# Create your views here.

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    

@csrf_exempt
def answer(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say('Hello!, This is Fahad Calling you from MedCheck. I am calling to check on your health. Please respond with your symptoms. Also let me know if you have any other health concerns.')
    return HttpResponse(str(vr), content_type='text/xml')
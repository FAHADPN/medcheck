from rest_framework import serializers
from .serializers import recordingSerializer
from .models import recording
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ehr.models import Patient
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
from decouple import config
from ehr.serializers import PatientSerializer

class recordingViewSet(viewsets.ModelViewSet):
    queryset = recording.objects.all()
    serializer_class = recordingSerializer

@api_view(['POST'])
def recording(request):
    data = request.data
    patient = Patient.objects.get(id=1)
    recording.objects.create(patient=patient, recording=data['recording'])
    return Response({'status': 'recording created'})


# Django APIs for handling Twilio IVR flow and OpenAI GPT
openai.api_key = config('OPENAI_API_KEY')

# Twilio IVR Flow using Python
@api_view(['POST', 'GET'])
def ivr_flow(request):
    # Create a Twilio Voice Response Object
    response = VoiceResponse()

    # Gather Input for Main Menu: Emergency or Appointment
    gather = Gather(
        input='speech dtmf',
        num_digits=1,
        action='/process-main-menu',
        method='POST',
        timeout=5,
        language='en-IN'
    )
    gather.say("Hello, welcome to Help Thou Me, your healthcare assistant. "
               "For emergency, press 1 or say 'emergency'. For appointments, press 2 or say 'appointment'.")
    
    # Add gather step to the response
    response.append(gather)

    return str(response)

@api_view(['POST', 'GET'])
def process_main_menu(request):
    """Handles the main menu input: emergency or appointment."""
    digits = request.values.get('Digits', None)
    speech_result = request.values.get('SpeechResult', '').lower()

    response = VoiceResponse()

    if digits == '1' or 'emergency' in speech_result:
        response.say("You selected Emergency. Connecting you to support.")
        response.dial("+917736968958")
    elif digits == '2' or 'appointment' in speech_result:
        gather = Gather(
            input='speech dtmf',
            num_digits=1,
            action='/identify-user',
            method='POST',
            timeout=5,
            language='en-IN'
        )
        gather.say("To schedule your appointment, if you're an existing patient with a patient ID, press 1. "
                   "If you're a new customer, press 2.")
        response.append(gather)
    else:
        response.redirect('/')

    return str(response)

@api_view(['POST', 'GET'])
def identify_user(request):
    """Identifies the user by patient ID or new customer."""
    digits = request.values.get('Digits', None)

    response = VoiceResponse()

    if digits == '1':
        gather = Gather(
            input='speech dtmf',
            finish_on_key='#',
            action='/get-patient-id',
            method='POST',
            language='en-IN'
        )
        gather.say("Please enter your patient ID followed by the hash key.")
        response.append(gather)
    elif digits == '2':
        gather = Gather(
            input='speech',
            action='/get-new-user-info',
            method='POST',
            language='en-IN'
        )
        gather.say("Please say your name.")
        response.append(gather)
    else:
        response.redirect('/identify-user')

    return str(response)

@api_view(['POST', 'GET'])
def get_patient_id(request):
    """Handles patient ID entry and forwards to the next step."""
    patient_id = request.values.get('Digits', None)
    # Call an API to fetch patient information based on ID.

    try:
        patient = Patient.objects.get(patient_id=patient_id)
        patient_serializer = PatientSerializer(patient)
        patient_info = patient_serializer.data
    except Patient.DoesNotExist:
        patient_info = None
    # Example: make API call to '/get_patient_info' with patient_id
    
    response = VoiceResponse()
    if not patient_info:
        response.say("Sorry, we couldn't find any patient with the provided ID. Please try again.")
        response.redirect('/identify-user')
        return str(response)
    else:
        response.say(f"Thank you! We have identified your patient ID as {patient_id}.")
        response.redirect('/gather-symptoms')

    return str(response)



@api_view(['POST', 'GET'])
def get_new_user_info(request):
    """Handles new user name collection."""
    user_name = request.values.get('SpeechResult', None)

    response = VoiceResponse()
    gather = Gather(
        input='speech dtmf',
        num_digits=2,
        action='/gather-symptoms',
        method='POST',
        language='en-IN'
    )
    response.say(f"Thank you {user_name}. Please enter your age.")
    response.append(gather)

    return str(response)

@api_view(['POST', 'GET'])
def gather_symptoms(request):
    """Handles gathering patient symptoms using AI in real-time."""
    response = VoiceResponse()

    # Step-by-step conversation asking about symptoms using AI
    conversation_history = request.values.get('SpeechResult', '')  # Past symptoms

    # Use OpenAI GPT to generate the next question based on the conversation
    ai_question = generate_next_symptom_question(conversation_history)
    
    gather = Gather(
        input='speech',
        action='/process-symptom-response',
        method='POST',
        language='en-IN'
    )
    gather.say(ai_question)
    response.append(gather)

    return str(response)

def generate_next_symptom_question(history):
    """Generates the next question based on patient symptom history using OpenAI."""
    prompt = f"Given the patient's symptoms: {history}, what should be the next step question to gather more info?"
    
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    return completion.choices[0].text.strip()

@api_view(['POST', 'GET'])
def process_symptom_response(request):
    """Processes the symptom response and gives further instruction."""
    response = VoiceResponse()
    symptoms = request.values.get('SpeechResult', '')

    # Append new symptoms to conversation history and ask further questions if needed
    response.say(f"Thanks for sharing your symptoms: {symptoms}. Our AI is analyzing the information.")

    # Send symptoms for analysis or escalate the call based on severity.
    response.redirect('/finalize-diagnosis')

    return str(response)

@api_view(['POST', 'GET'])
def finalize_diagnosis(request):
    """Final step after gathering all the symptoms."""
    response = VoiceResponse()
    response.say("Thank you for your patience. Based on your symptoms, we will provide further instructions soon.")
    response.hangup()

    return str(response)

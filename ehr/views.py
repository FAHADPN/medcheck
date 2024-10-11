# from django.shortcuts import render
# from rest_framework import viewsets
# from .models import Patient
# from .serializers import PatientSerializer
# Create your views here.

# class PatientViewSet(viewsets.ModelViewSet):
#     queryset = Patient.objects.all()
#     serializer_class = PatientSerializer
    

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.voice_response import VoiceResponse, Gather
from django.core.cache import cache
from django.utils import timezone
import uuid
import openai
from decouple import config

from .models import Patient, CallLog

openai.api_key = config('OPENAI_API_KEY')

def generate_call_id(request):
    call_sid = request.POST.get('CallSid')
    if not call_sid:
        call_sid = str(uuid.uuid4())
    return call_sid

def save_step_data(call_id, step_name, data):
    call_data = cache.get(call_id, {})
    call_data[step_name] = data
    cache.set(call_id, call_data, timeout=3600)  # Store for 1 hour

def get_call_data(call_id):
    return cache.get(call_id, {})

@csrf_exempt
def welcome(request: HttpRequest) -> HttpResponse:
    call_id = generate_call_id(request)
    save_step_data(call_id, 'call_start', {
        'caller_number': request.POST.get('From', ''),
        'timestamp': timezone.now()
    })

    vr = VoiceResponse()
    vr.say("Hello, Thanks for calling \"Help Thou me\" your Healthcare assistant.", voice="Polly.Aditi", language="en-IN")
    
    gather = Gather(
        num_digits=1,
        action=reverse('handle_initial_choice') + f'?call_id={call_id}',
        timeout=5,
        language="en-IN"
    )
    gather.say("For emergency press 1 or say emergency. For Appointments press 2 or say Appointment", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('welcome') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_initial_choice(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    choice = request.POST.get('Digits', '')
    speech_result = request.POST.get('SpeechResult', '').lower()

    save_step_data(call_id, 'initial_choice', {
        'digits': choice,
        'speech_result': speech_result
    })

    vr = VoiceResponse()

    if choice == '1' or 'emergency' in speech_result:
        vr.say("Connecting you to support.", voice="Polly.Aditi", language="en-IN")
        vr.dial('+917736968958', caller_id=request.POST.get('From', ''))
    elif choice == '2' or 'appointment' in speech_result:
        vr.redirect(reverse('gather_user_identification') + f'?call_id={call_id}')
    else:
        vr.redirect(reverse('welcome') + f'?call_id={call_id}')

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def gather_user_identification(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    vr = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=reverse('handle_user_identification') + f'?call_id={call_id}',
        timeout=5,
        language="en-IN"
    )
    gather.say("To schedule your appointment we need to identify you. If you are an existing customer with patient id press 1 or say patient id. If you are a new customer press 2 or say new customer.", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('gather_user_identification') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_user_identification(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    choice = request.POST.get('Digits', '')
    speech_result = request.POST.get('SpeechResult', '').lower()

    save_step_data(call_id, 'user_identification', {
        'digits': choice,
        'speech_result': speech_result
    })

    vr = VoiceResponse()

    if choice == '1' or 'patient id' in speech_result:
        vr.redirect(reverse('gather_ehr_id') + f'?call_id={call_id}')
    elif choice == '2' or 'new customer' in speech_result:
        vr.redirect(reverse('gather_username') + f'?call_id={call_id}')
    else:
        vr.redirect(reverse('gather_user_identification') + f'?call_id={call_id}')

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def gather_ehr_id(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    vr = VoiceResponse()
    gather = Gather(
        finish_on_key='#',
        action=reverse('handle_ehr_id') + f'?call_id={call_id}',
        timeout=5,
        language="en-IN"
    )
    gather.say("Please type your patient id you obtained during your registration and end with a hash key.", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('gather_ehr_id') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_ehr_id(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    ehr_id = request.POST.get('Digits', '')
    
    save_step_data(call_id, 'ehr_id', {
        'digits': ehr_id
    })

    patient_data = Patient.objects.get(id=ehr_id)
    if not patient_data:
        vr = VoiceResponse()
        vr.say("Sorry, we could not find a patient with the provided ID. Please try again.", voice="Polly.Aditi", language="en-IN")
        vr.redirect(reverse('gather_user_identification') + f'?call_id={call_id}')
        return HttpResponse(str(vr), content_type='text/xml')
    # Here you would typically validate the EHR ID and retrieve patient information
    # For this example, we'll just move to symptom collection
    vr = VoiceResponse()
    vr.redirect(reverse('gather_symptoms') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def gather_username(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    vr = VoiceResponse()
    gather = Gather(
        input='speech',
        action=reverse('confirm_username') + f'?call_id={call_id}',
        timeout=5,
        language="en"
    )
    gather.say("Please say your name.", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('gather_username') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def confirm_username(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    username = request.POST.get('SpeechResult', '')
    
    save_step_data(call_id, 'username', {
        'speech_result': username
    })

    vr = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=reverse('handle_username_confirmation') + f'?call_id={call_id}',
        timeout=5,
        language="en"
    )
    gather.say(f"Please press 1 to confirm your name is {username}", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('confirm_username') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_username_confirmation(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    choice = request.POST.get('Digits', '')
    vr = VoiceResponse()

    if choice == '1':
        vr.redirect(reverse('gather_age') + f'?call_id={call_id}')
    else:
        vr.redirect(reverse('gather_username') + f'?call_id={call_id}')

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def gather_age(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    vr = VoiceResponse()
    gather = Gather(
        num_digits=2,
        action=reverse('confirm_age') + f'?call_id={call_id}',
        timeout=5,
        language="en"
    )
    gather.say("Please type your age in the keypad.", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('gather_age') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def confirm_age(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    age = request.POST.get('Digits', '')
    
    save_step_data(call_id, 'age', {
        'digits': age
    })

    vr = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=reverse('handle_age_confirmation') + f'?call_id={call_id}',
        timeout=5,
        language="en"
    )
    gather.say(f"Your age is {age}. Please confirm your age by pressing 1. Press 2 to re-enter your age.", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('confirm_age') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_age_confirmation(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    choice = request.POST.get('Digits', '')
    vr = VoiceResponse()

    if choice == '1':
        vr.redirect(reverse('gather_user_number') + f'?call_id={call_id}')
    elif choice == '2':
        vr.redirect(reverse('gather_age') + f'?call_id={call_id}')
    else:
        vr.redirect(reverse('confirm_age') + f'?call_id={call_id}')

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def gather_user_number(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    vr = VoiceResponse()
    gather = Gather(
        num_digits=1,
        action=reverse('handle_user_number') + f'?call_id={call_id}',
        timeout=5,
        language="en"
    )
    caller_number = request.POST.get('From', '')
    gather.say(f"Please confirm that you are calling from the phone number you choose to register. The number is {caller_number}. Press 1 to confirm. If not the correct phone number, press 2 to end the call.", voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('gather_user_number') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_user_number(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    choice = request.POST.get('Digits', '')
    
    save_step_data(call_id, 'user_number', {
        'digits': choice
    })

    vr = VoiceResponse()

    if choice == '1':
        vr.redirect(reverse('create_patient') + f'?call_id={call_id}')
    elif choice == '2':
        vr.say("Thank you for calling. Goodbye.", voice="Polly.Aditi", language="en-IN")
        vr.hangup()
    else:
        vr.redirect(reverse('gather_user_number') + f'?call_id={call_id}')

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def create_patient(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    call_data = get_call_data(call_id)

    # Create a new Patient instance
    patient = Patient.objects.create(
        name=call_data.get('username', {}).get('speech_result', ''),
        age=int(call_data.get('age', {}).get('digits', 0)),
        phone_number=call_data.get('call_start', {}).get('caller_number', '')
    )

    # Create a CallLog instance
    CallLog.objects.create(
        patient=patient,
        call_sid=call_id,
        initial_choice=call_data.get('initial_choice', {}).get('digits', ''),
        user_identification=call_data.get('user_identification', {}).get('digits', ''),
        ehr_id=call_data.get('ehr_id', {}).get('digits', ''),
        symptoms=''  # This will be updated after gathering symptoms
    )

    vr = VoiceResponse()
    vr.redirect(reverse('gather_symptoms') + f'?call_id={call_id}')
    return HttpResponse(str(vr), content_type='text/xml')

def generate_next_question(conversation_history):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a medical assistant gathering information about a patient's symptoms. Ask concise, relevant questions based on the conversation history. Limit your response to just the next question."},
            {"role": "user", "content": f"Conversation history: {conversation_history}\n\nWhat should be the next question?"}
        ]
    )
    return response.choices[0].message['content']

@csrf_exempt
def gather_symptoms(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    question_number = int(request.GET.get('question_number', '0'))
    conversation_history = get_call_data(call_id).get('conversation_history', [])

    vr = VoiceResponse()

    if question_number == 0:
        question = "Please describe your main symptom or concern."
    elif question_number >= 10:
        vr.redirect(reverse('handle_symptoms') + f'?call_id={call_id}')
        return HttpResponse(str(vr), content_type='text/xml')
    else:
        question = generate_next_question(conversation_history)

    gather = Gather(
        input='speech',
        action=reverse('handle_symptoms') + f'?call_id={call_id}&question_number={question_number}',
        timeout=10,
        language="en-IN"
    )
    gather.say(question, voice="Polly.Aditi", language="en-IN")
    vr.append(gather)

    vr.redirect(reverse('gather_symptoms') + f'?call_id={call_id}&question_number={question_number}')
    return HttpResponse(str(vr), content_type='text/xml')

@require_POST
@csrf_exempt
def handle_symptoms(request: HttpRequest) -> HttpResponse:
    call_id = request.GET.get('call_id')
    question_number = int(request.GET.get('question_number', '0'))
    answer = request.POST.get('SpeechResult', '')

    conversation_history = get_call_data(call_id).get('conversation_history', [])
    conversation_history.append(f"Q{question_number}: {answer}")
    save_step_data(call_id, 'conversation_history', conversation_history)

    vr = VoiceResponse()

    if question_number >= 9:
        # Update the CallLog with symptoms
        call_log = CallLog.objects.get(call_sid=call_id)
        call_log.symptoms = "\n".join(conversation_history)
        call_log.save()

        vr.say("Thank you for providing your symptoms. We will process this information and get back to you with an appointment. Goodbye.", voice="Polly.Aditi", language="en-IN")
        vr.hangup()
    else:
        vr.redirect(reverse('gather_symptoms') + f'?call_id={call_id}&question_number={question_number + 1}')

    return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def error_inconvinience(request: HttpRequest) -> HttpResponse:
    vr = VoiceResponse()
    vr.say("Sorry, we are currently facing some issues. Please try again later.", voice="Polly.Aditi", language="en-IN")
    vr.hangup()
    return HttpResponse(str(vr), content_type='text/xml')
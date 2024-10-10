from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recordingViewSet, recording, ivr_flow, process_main_menu 
from .views import identify_user, get_new_user_info, gather_symptoms
from .views import process_symptom_response,finalize_diagnosis,get_patient_id

router = DefaultRouter()
router.register(r"recording", recordingViewSet)
router.register(r"ivr_flow", ivr_flow)
router.register(r"process_main_menu", process_main_menu)
router.register(r"identify_user", identify_user)
router.register(r"get_new_user_info", get_new_user_info)
router.register(r"get_patient_id", get_patient_id)
router.register(r"gather_symptoms", gather_symptoms)
router.register(r"process_symptoms", process_symptom_response)
router.register(r"finalize_diagnosis", finalize_diagnosis)

urlpatterns = [
    path("recording/", recording, name="recording"),
    # path('conversation/<str:session_id>/', ivr_conversation, name='ivr_conversation'),
    path("", include(router.urls)),
]
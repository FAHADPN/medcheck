from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import recordingViewSet, recording, ivr_flow, process_main_menu 
from .views import identify_user, get_new_user_info, gather_symptoms
from .views import process_symptom_response,finalize_diagnosis,get_patient_id

# router = DefaultRouter()
urlpatterns = [
    path("recording/", recording, name="recording"),
    path("ivr_flow/", ivr_flow, name="ivr_flow"),
    path("process_main_menu/", process_main_menu, name="process_main_menu"),
    path("identify_user/", identify_user, name="identify_user"),
    path("get_new_user_info/", get_new_user_info, name="get_new_user_info"),
    path("get_patient_id/", get_patient_id, name="get_patient_id"),
    path("gather_symptoms/", gather_symptoms, name="gather_symptoms"),
    path("process_symptoms/", process_symptom_response, name="process_symptom_response"),
    path("finalize_diagnosis/", finalize_diagnosis, name="finalize_diagnosis"),
]

# urlpatterns = [
#     path("recording/", recording, name="recording"),
#     # path('conversation/<str:session_id>/', ivr_conversation, name='ivr_conversation'),
#     path("", include(router.urls)),
# ]
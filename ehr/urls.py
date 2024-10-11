from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import PatientViewSet, answer
from . import views

# Create a router and register the viewset
# router = DefaultRouter()
# router.register(r'patients', PatientViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('handle-initial-choice/', views.handle_initial_choice, name='handle_initial_choice'),
    path('gather-user-identification/', views.gather_user_identification, name='gather_user_identification'),
    path('handle-user-identification/', views.handle_user_identification, name='handle_user_identification'),
    path('gather-ehr-id/', views.gather_ehr_id, name='gather_ehr_id'),
    path('handle-ehr-id/', views.handle_ehr_id, name='handle_ehr_id'),
    path('gather-username/', views.gather_username, name='gather_username'),
    path('confirm-username/', views.confirm_username, name='confirm_username'),
    path('handle-username-confirmation/', views.handle_username_confirmation, name='handle_username_confirmation'),
    path('gather-age/', views.gather_age, name='gather_age'),
    path('confirm-age/', views.confirm_age, name='confirm_age'),
    path('handle-age-confirmation/', views.handle_age_confirmation, name='handle_age_confirmation'),
    path('gather-user-number/', views.gather_user_number, name='gather_user_number'),
    path('handle-user-number/', views.handle_user_number, name='handle_user_number'),
    path('create-patient/', views.create_patient, name='create_patient'),
    path('doctor_department/', views.doctor_department, name='doctor_department'),
    path('schedule-appointment/', views.schedule_appointment, name='schedule_appointment'),
    path('gather-symptoms/', views.gather_symptoms, name='gather_symptoms'),
    path('handle-symptoms/', views.handle_symptoms, name='handle_symptoms'),
    path('error/', views.error_inconvinience, name='error'),
]
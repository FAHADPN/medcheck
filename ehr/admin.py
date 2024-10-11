from django.contrib import admin
from .models import Patient, CallLog
# Register your models here.
admin.site.register(Patient)
admin.site.register(CallLog)
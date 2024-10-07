from django.db import models
from ehr.models import Patient
# Create your models here.
class recording(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    recording = models.CharField(max_length=200)
from django.db import models

# Create your models here.

class Patient(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    phone = models.CharField(max_length=25, blank=True)

    class Meta:
        unique_together = ('name', 'age', 'phone')  # Ensure the co mbination is unique

    def __str__(self):
        return f"{self.name}, Age: {self.age}, Phone: {self.phone}"
    

class CallLog(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    call_sid = models.CharField(max_length=100, unique=True)
    initial_choice = models.CharField(max_length=1)
    user_identification = models.CharField(max_length=1)
    ehr_id = models.CharField(max_length=50, blank=True)
    symptoms = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
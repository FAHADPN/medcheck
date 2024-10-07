from django.db import models

# Create your models here.

class Patient(models.Model):
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    phone = models.CharField(max_length=25, blank=True)

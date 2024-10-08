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
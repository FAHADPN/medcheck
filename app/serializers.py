from .models import recording
from rest_framework import serializers

class recordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = recording
        fields = '__all__'

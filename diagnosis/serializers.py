from rest_framework import serializers
from .models import UserDiagnosisRequest


class UserDiagnosisRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDiagnosisRequest
        fields = '__all__'

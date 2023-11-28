from rest_framework import serializers
from .models import UserDiagnosisResult


class UserReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDiagnosisResult
        fields = '__all__'


class UserReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDiagnosisResult
        fields = ['id', 'request_user_id', 'request_id', 'crop_category', 'crop_status', 'created_date']

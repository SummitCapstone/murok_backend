from rest_framework import serializers
from .models import RequestUser


class RequestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestUser
        fields = '__all__'
        read_only_fields = ('id', 'first_request_date', 'last_request_date', )

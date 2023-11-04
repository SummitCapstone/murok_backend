from django.shortcuts import render
from pathlib import Path

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from diagnosis.serializers import UserDiagnosisRequestSerializer


# Create your views here.


class UserRequestDiagnosis(APIView):
    permission_classes = (AllowAny,) # Unregistered User permission should be added.
    parser_classes = (MultiPartParser, FormParser, )

    def post(self, request: Request) -> Response:
        request.META: dict
        try:
            requested_user = request.META.get('X-User-Id', None)
            if requested_user is None:
                raise ValueError('Invalid User')
        except ValueError:
            return Response({'error': 'Invalid User'}, status=400)

        request.data['requested_user_id'] = requested_user

        serializer = UserDiagnosisRequestSerializer(data=request.data)

        # This below code will be replaced to request to ML server soon.
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Request Received'}, status=200)

from django.shortcuts import render
from pathlib import Path

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication

from diagnosis.models import UserDiagnosisRequest
from diagnosis.serializers import UserDiagnosisRequestSerializer
from accounts.models import User
from murok_backend import settings

import uuid

# Create your views here.
'''
비로그인 사용자 : 프론트엔드 앱에서 만든 uuid만 보냄
로그인 사용자 : 프론트엔드 앱에서 만든 uuid 외에도 JWT 토큰도 보냄

* Authentication Flow
1. Check whether the request contains UUID or not.

1-1. If the request contains UUID, check whether the UUID is valid or not.

1-1-1. If the UUID is valid, check whether the UUID is already registered or not.

'''


class UserRequestDiagnosis(APIView):
    permission_classes = (AllowAny, IsAuthenticated,)  # Unregistered User permission should be added.
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request: Request) -> Response:

        # Validate token and extract user_id from it, if the token is provided and valid.
        try:
            # This can be cached in memory database for performance; Maybe caching in Django?
            jwt_auth = JWTAuthentication()

            auth_header = request.META.get('HTTP_AUTHORIZATION', None)
            # Non-registered user flow
            if auth_header is None:
                # Go to non-registered user flow
                pass

            if not request.user.is_authenticated:
                raise

            user_id = jwt_auth.get_user(auth_header)
            if user_id is None:
                raise ValueError('Valid JWT token is not provided.', 400)
            # 비회원 -> 보낸 uuid로 저장
            # 회원 -> 회원 id로 저장

        except ValueError as err:
            return Response({'error': f'{err}'}, status=400)

        # Validate request_id
        try:
            request_id = request.META.get('HTTP_X_REQUEST_ID', None)
            if request_id is None:
                raise ValueError('Valid Request ID is not provided.', 400)

            # Convert str type UUID to uuid.UUID object
            request_uuid = uuid.UUID(request_id)

            # Validate UUID format of request_id
            if not uuid.UUID(request_id):
                raise ValueError('Valid Request ID is not provided.', 400)

            # Check whether the request_id is already registered or not.
            if UserDiagnosisRequest.objects.filter(request_uuid=request_uuid).exists():
                # Not in Debug Mode, Raise an exception.
                if not settings.DEBUG:
                    raise ValueError('Invalid Request ID.', 400)
                else:
                    UserDiagnosisRequest.objects.filter(request_uuid=request_uuid).delete()
        except ValueError as err:
            return Response({'error': f'{err}'}, status=400)

        serializer = UserDiagnosisRequestSerializer(data=request.data)

        # This below code will be replaced to request to ML server soon.
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Request Received'}, status=200)

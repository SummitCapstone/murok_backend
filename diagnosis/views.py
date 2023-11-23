import traceback
from types import NoneType

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
from accounts.models import User, RequestUser
from murok_backend import settings
from murok_backend.permissions import IsValidUser

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
    permission_classes = (IsValidUser,)  # Unregistered User permission should be added.
    parser_classes = (MultiPartParser, FormParser,)
    authentication_classes = (JWTAuthentication,)

    def post(self, request: Request) -> Response:
        """
        Send a diagnosis request to server.
        :param request: Request object
        :return: Response object with status code
        """

        # Queue using Celery and RabbitMQ or Redis... (Not implemented yet)

        # Validate request_id
        try:
            request_id = request.META.get('HTTP_X_REQUEST_ID', None)
            if request_id is None:
                raise ValueError

            # Convert str type UUID to uuid.UUID object
            request_uuid = uuid.UUID(request_id)

            # Check whether the request_id is already registered or not.
            if UserDiagnosisRequest.objects.filter(request_uuid=request_uuid).exists():
                # Not in Debug Mode, Raise an exception.
                if not settings.DEBUG:
                    raise ValueError
                else:
                    UserDiagnosisRequest.objects.filter(request_uuid=request_uuid).delete()
        except ValueError:
            return Response({'code': 400, 'message': 'Valid Request ID is not provided.'}, status=400)


        # Extract request_user_uuid from request header
        try:
            request_user_uuid = request.META.get('HTTP_X_REQUEST_USER_ID', None)
            if request_user_uuid is None:
                raise ValueError
            request_user_uuid = uuid.UUID(request_user_uuid, version=400)
        except ValueError as err:
            traceback.print_exc()
            return Response({'code': 400, 'message': 'Valid Request user\'s UUID is not provided.'}, status=400)

        # Get User object from request.user
        user = request.user
        user_id = None
        if isinstance(user, User):
            user: User
            user_id = user.id
            user_id: uuid.UUID or NoneType

        # Find a request user in RequestUser table
        try:
            request_user = RequestUser.objects.get(id=request_user_uuid)
        except RequestUser.DoesNotExist:
            # If the request user does not exist, create a new request user.
            if isinstance(user, User):
                request_user = RequestUser.objects.create_user(id=request_user_uuid, user=user)
            else:
                request_user = RequestUser.objects.create_user(id=request_user_uuid)
        finally:
            # If the request user exists, update last_request_date field.
            request_user.save()

        request.data['id'] = request_uuid
        request.data['request_user_id'] = request_user.id

        # Save the request to UserDiagnosisRequest table
        serializer = UserDiagnosisRequestSerializer(data=request.data)

        # This below code will be replaced to request to ML server soon.
        if serializer.is_valid():
            serializer.save()
            return Response({'code': 200, 'message': 'Your request is successfully sent. Wait for seconds!'}
                            , status=200)
        else:
            request.user.delete()
            return Response({'code': 500, 'message': 'Internal Server Error.'}, status=500)

import traceback
from types import NoneType

from django.shortcuts import render
from pathlib import Path

import requests
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
from murok_backend.settings import BASE_DIR, AI_SERVER_URL
from .models import CropCategory
# from .tasks import send_diagnosis_data_to_aiserver
from reports.models import UserDiagnosisResult, CropStatus, translate_crop_status

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


class AIServerError(Exception):
    def __init__(self, message: str, extra_info: dict = None):
        super().__init__()
        self.extra_info = extra_info

    def __str__(self):
        return f'{super().__str__()} (AI Server information: {self.extra_info})'


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
            if UserDiagnosisRequest.objects.filter(id=request_uuid).exists():
                # Not in Debug Mode, Raise an exception.
                if not settings.DEBUG:
                    raise ValueError
                else:
                    UserDiagnosisRequest.objects.filter(id=request_uuid).delete()
        except ValueError:
            return Response({'code': 400, 'message': 'Valid Request ID is not provided.'}, status=400)

        # Extract request_user_uuid from request header
        try:
            request_user_uuid = request.META.get('HTTP_X_REQUEST_USER_ID', None)
            if request_user_uuid is None:
                raise ValueError
            request_user_uuid_validated = uuid.UUID(request_user_uuid, version=4)
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
            request_user.save()
        except RequestUser.DoesNotExist:
            # If the request user does not exist, create a new request user.
            if isinstance(user, User):
                request_user = RequestUser.objects.create(id=request_user_uuid, registered_user=user)
            else:
                request_user = RequestUser.objects.create(id=request_user_uuid)

        final_data = request.data.copy()
        final_data['id'] = request_uuid
        final_data['request_user_id'] = request_user.id

        # Save the request to UserDiagnosisRequest table
        serializer = UserDiagnosisRequestSerializer(data=final_data)
        entity = None

        # This below code will be replaced to request to ML server soon.
        if serializer.is_valid():
            entity = serializer.save()

            # Request a task to RabbitMQ to send the image to AI server.
            # send_diagnosis_data_to_aiserver.send(request_uuid, request_user_uuid, serializer.validated_data['crop_category'])
            try:
                result_entity = send_diagnosis_data_to_aiserver_non_rabbitmq(entity,
                                                                             serializer.validated_data['crop_category'])
            except AIServerError:
                entity.delete()
                return Response({'code': 500, 'message': 'Internal Server Error.'}, status=500)

            return Response({'code': 200, 'result_url': f'/diagnosis/result/{request_uuid.hex}'}, status=200)
        else:
            request_user.delete()
            return Response({'code': 500, 'message': 'Internal Server Error.'}, status=500)


def send_diagnosis_data_to_aiserver_non_rabbitmq(request_entity: UserDiagnosisRequest,
                                                 crop_category: CropCategory) -> UserDiagnosisResult:
    try:
        diagnosis_original_request = request_entity
        # Get an absolute path of the image file

        file_path = BASE_DIR / diagnosis_original_request.picture.path
        # Decapitalize letter
        crop_category = crop_category.lower()
        str_data = {'crop_type': crop_category}
        # Send the image file to the AI server
        with open(file_path, 'rb') as f:
            image_file = {'image': (str(file_path), f)}
            diagnosis_result = requests.post(AI_SERVER_URL, files=image_file, data=str_data)

        print(diagnosis_result.status_code)
        print(diagnosis_result)
        diagnosis_result: requests.Response
        disease_ranking = diagnosis_result.json()['top_diseases']
        disease_possibility_ranking = diagnosis_result.json()['top_probabilities']

        # Serialize the ranking data
        ranking, crop_stat = serialize_ranking(disease_possibility_ranking, disease_ranking)

        # Make a new entity of UserDiagnosisResult
        result = UserDiagnosisResult.objects.create(
            id=uuid.uuid4().hex,
            request_user_id=RequestUser.objects.get(id=str(diagnosis_original_request.request_user_id.id)),
            request_id=UserDiagnosisRequest.objects.get(id=str(diagnosis_original_request.id)),
            crop_category=crop_category,
            crop_status=crop_stat,
            probability_ranking=ranking
        )
    except Exception:
        # Print stack trace
        traceback.print_exc()
        raise AIServerError('AI Server Error')
    else:
        return result
    # Send the image to AI server.


def serialize_ranking(possibility_ranking: list[float], disease_ranking: list[str]) -> tuple[list[dict[str, int | str]], CropCategory or str]:
    """
    Serialize the ranking data to JSON format.
    :param possibility_ranking: Possibility ranking data
    :param disease_ranking: Disease ranking data
    :return: Serialized ranking data
    """
    # Make a list of dictionaries
    # [
    #     {
    #         "rank": 1,
    #         "state": "HEALTHY",
    #         "probability": "80.2"
    #     },
    #     {
    #         "rank": 2,
    #         "state": "STRAWBERRY_LEAF_SCORCH",
    #         "probability": "19.8"
    #     }
    # ]
    ranking = []
    for i in range(len(possibility_ranking)):
        entity = {
            'rank': i + 1,
            'state': disease_ranking[i],
            'probability': str(possibility_ranking[i])
        }
        ranking.append(entity)

    translated_disease = translate_crop_status(disease_ranking[0])

    # Convert disease_ranking[0] to CropCategory
    return ranking, CropStatus[translated_disease]

import uuid
from enum import Enum

from django.db.models import QuerySet
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from murok_backend.permissions import IsValidUser, IsRequestUser
from reports.models import UserDiagnosisResult, CropStatus
from .serializers import UserReportSerializer
from murok_backend.pagination import UserReportListPagination
from diagnosis.models import UserDiagnosisRequest, CropCategory


class SortEnum(Enum):
    DEFAULT = 'default'
    LATEST = 'latest'
    OLDEST = 'oldest'


class ResultStateEnum(Enum):
    ABNORMAL = 'abnormal'
    NORMAL = 'normal'
    ALL = 'all'


def apply_criteria(targets: QuerySet, sort: SortEnum = SortEnum.DEFAULT,
                   crop: tuple[CropCategory] or None = None,
                   result: ResultStateEnum = ResultStateEnum.ALL) -> QuerySet:
    match sort:
        case SortEnum.OLDEST:
            targets = targets.order_by('created_date')
        case _: # SortEnum.DEFAULT, SortEnum.LATEST
            targets = targets.order_by('-created_date')

    if isinstance(crop, tuple):
        targets = targets.filter(crop_category__in=crop)

    match result:
        case ResultStateEnum.ABNORMAL:
            targets = targets.exclude(crop_status=CropStatus.HEALTHY)
        case _:
            targets = targets.filter(crop_status=CropStatus.HEALTHY)

    return targets


'''
class UserReportListAdminView(APIView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)
    pagination_class = UserReportListPagination
'''

class UserReportListView(APIView):
    permission_classes = (IsAdminUser, IsAuthenticated)
    authentication_classes = (JWTAuthentication,)
    pagination_class = UserReportListPagination

    def get(self, request: Request, result_id: str):

        # Parse parameters
        page = request.GET.get('page', 1)
        sort = request.GET.get('sort', 'default')
        crop = request.GET.get('crop_category', None)
        result = request.GET.get('result', 'abnormal')
        # start_date = request.GET.get('start_date', None)
        # end_date = request.GET.get('end_date', None)

        # Sort function

        targets = UserDiagnosisResult.objects.filter(request_user_id__registered_user=request.user)

        targets = apply_criteria(targets, sort, crop, result)

        # Pagination




        return Response({'code': 200, 'message': 'OK'}, status=200)


class UserReportDetailView(APIView):
    permission_classes = (IsAdminUser, IsRequestUser)
    authentication_classes = (JWTAuthentication,)

    def get(self, request: Request, result_id: str) -> Response:

        try:
            result_uuid = uuid.UUID(result_id, version=4)

        except ValueError:
            return Response({'code': 404, 'message': 'Not Found'}, status=404)

        report = UserDiagnosisResult.objects.get(id=str(result_uuid))

        serializer = UserReportSerializer(data=report)

        if serializer.is_valid():
            return Response(serializer.data, status=200)
        else:
            return Response({'code': 500, 'message': 'Internal Server Error'}, status=500)

    def delete(self, request: Request, result_id: str) -> Response:

        try:
            target = UserDiagnosisResult.objects.get(id=result_id)

            target_request = UserDiagnosisRequest.objects.get(id=str(target.request_id))
            target_request.delete()
            target.delete()

            return Response({'code': 200, 'message': 'Successfully deleted'}, status=200)
        except UserDiagnosisResult.DoesNotExist:
            return Response({'code': 404, 'message': 'Not Found'}, status=404)
        except UserDiagnosisRequest.DoesNotExist:
            return Response({'code': 404, 'message': 'Not Found'}, status=404)

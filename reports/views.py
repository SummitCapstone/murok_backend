import uuid
from enum import Enum

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from murok_backend.permissions import IsValidUser, IsRequestUser
from reports.models import UserDiagnosisResult, CropStatus
from .serializers import UserReportSerializer, UserReportListSerializer
from murok_backend.pagination import UserReportListPagination
from diagnosis.models import UserDiagnosisRequest, CropCategory
from rest_framework.pagination import PageNumberPagination


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
            targets = targets.exclude(crop_status=CropStatus.UNHEALTHY)
        case ResultStateEnum.NORMAL:
            targets = targets.filter(crop_status=CropStatus.HEALTHY)

    return targets


'''
class UserReportListAdminView(APIView):
    permission_classes = (IsAdminUser,)
    authentication_classes = (JWTAuthentication,)
    pagination_class = UserReportListPagination
'''


class UserReportListView(APIView):
    permission_classes = (IsValidUser,)
    authentication_classes = (JWTAuthentication,)
    pagination_class = UserReportListPagination

    class UserReportListPagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = 'page_size'
        max_page_size = 100

    def get(self, request: Request):
        # Parse parameters
        sort = request.GET.get('sort', 'default')
        crop = request.GET.get('crop_category', None)
        result = request.GET.get('result', 'all')

        try:
            user_uuid = request.META.get('HTTP_X_REQUEST_USER_ID', None)


            user_uuid = uuid.UUID(user_uuid, version=4)
        except ValueError:
            return Response({'code': 400, 'message': 'Invalid Request User ID'}, status=400)
        else:
            # Check registered user
            if not isinstance(request.user, AnonymousUser):
                targets = UserDiagnosisResult.objects.filter(request_user_id__registered_user__id=str(request.user.id))
            else:
                # Filter targets
                targets = UserDiagnosisResult.objects.filter(request_user_id=str(user_uuid))
            targets = apply_criteria(targets, sort, crop, result)

        # Paginate results
        paginator = self.pagination_class()
        paginated_targets = paginator.paginate_queryset(targets, request)

        # Serialize results
        serializer = UserReportListSerializer(paginated_targets, many=True)

        return paginator.get_paginated_response(serializer.data)


class UserReportDetailView(APIView):
    permission_classes = (IsRequestUser,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request: Request, result_id: str) -> Response:

        try:
            result_uuid = uuid.UUID(result_id, version=4)

        except ValueError:
            return Response({'code': 404, 'message': 'Not Found'}, status=404)

        report = UserDiagnosisResult.objects.get(id=str(result_uuid))

        serializer = UserReportSerializer(report)

        return Response(serializer.data, status=200)

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

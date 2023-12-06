from uuid import UUID
from typing import Any
from rest_framework.request import Request
from rest_framework.permissions import BasePermission

from accounts.models import RequestUser, User
from diagnosis.models import UserDiagnosisRequest
from reports.models import UserDiagnosisResult
from django.shortcuts import get_object_or_404


class IsValidUser(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        # Check X-Request-User-Id header and validate it
        try:
            val = request.META.get('HTTP_X_REQUEST_USER_ID', None)

            if val is None:
                raise ValueError
            request_user_uuid = UUID(val)
        except ValueError:
            return False
        else:
            return True


# Equivalent to IsAuthenticated
class IsRegisteredUser(BasePermission):
    pass


# For unregistered user only (May NOT be used I guess)
class IsUnregisteredUser(BasePermission):
    pass


class IsRequestUser(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        # Check X-Request-User-Id header and validate it
        try:
            # Get request_user_id from request.META
            req_user_id = request.META.get('HTTP_X_REQUEST_USER_ID', None)

            if req_user_id is None:
                raise ValueError

            # Convert str type UUID to uuid.UUID object for validation.
            request_user_uuid = UUID(req_user_id, version=4)

            request_user = RequestUser.objects.get(id=str(request_user_uuid))
            

            # Get Report_id
            report_id = view.kwargs.get('result_id', None)

            if report_id is None:
                return False

            report_id = UUID(report_id, version=4)
            request_id = UserDiagnosisResult.objects.get(id=report_id).request_id.id


            # TODO: Revert to also verify registered user.
            # Check whether the report's original request user is the same as the request user.
            report = UserDiagnosisResult.objects.get(id=report_id)

            if str(report.request_user_id.id) == str(request_user.id):
                return True
            # If not matched, check whether the user is registered or not.
            # That's because the database could also save multiple request_user_id per one registered user's id
            # (e.g. the user requested diagnosis as a guest and then registered as a member)
            return False

            # Check whether the UserDiagnosisRequest entity 
        except ValueError:
            return False
        except RequestUser.DoesNotExist:
            return False

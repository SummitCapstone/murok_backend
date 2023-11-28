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
            

            # Get Request_id
            request_id = view.kwargs.get('request_id', None)
            report_id = view.kwargs.get('report_id', None)

            target_request_user_id = None

            # In case of requesting a report
            if request_id is None and report_id is not None:
                request_id = UserDiagnosisResult.objects.get(id=report_id).request_id.id
                # Message structure of Http404 should be changed..
                target_request_user_id = get_object_or_404(UserDiagnosisResult, id=request_id).request_user_id.id
            # In case of requesting a 'request' entity for review.
            elif request_id is not None and report_id is None:
                target_request_user_id = get_object_or_404(UserDiagnosisRequest, id=request_id).request_user_id.id
            else:
                raise ValueError
            
            if target_request_user_id is None:
                raise ValueError
            
            if request_user.id == target_request_user_id:
                view.request_user = request_user
                return True
            
            # Check whether the user is a registered user or not.
            registered_user = request.user
            if not isinstance(registered_user, User):
                return False
            
            user_side_user_id = RequestUser.objects.get(id=str(request_user.id),
                                                        registered_user__id=str(registered_user.id)).id
            server_side_user_id = RequestUser.objects.get(id=str(target_request_user_id),
                                                          registered_user__id=str(registered_user.id)).id

            return user_side_user_id == server_side_user_id

            # Check whether the UserDiagnosisRequest entity 
        except ValueError:
            return False
        except RequestUser.DoesNotExist:
            return False

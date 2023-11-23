from uuid import UUID
from rest_framework.request import Request
from rest_framework.permissions import BasePermission


class IsValidUser(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        # Check X-Request-User-Id header and validate it
        try:
            request_user_uuid = UUID(request.headers.get('X-Request-User-Id', None))
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

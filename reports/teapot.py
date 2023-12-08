from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from murok_backend.permissions import IsValidUser


class WhatIsThisTeapot(APIView):
    permission_classes = (IsValidUser,)

    def get(self, request: Request) -> Response:
        return Response({'code': 418, 'message': 'I\'m a teapot.'}, status=418)

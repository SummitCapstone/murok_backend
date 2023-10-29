import logging
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drfpasswordless.serializers import CallbackTokenAuthSerializer
from drfpasswordless.settings import api_settings


# logger = logging.getLogger(__name__)

class ObtainJWTTokenFromCallbackToken(APIView):
    """
    Returns JWT Token(access, refresh) based on our callback token and source.
    """
    permission_classes = (AllowAny,)
    serializer_class = CallbackTokenAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # 인증 코드(callback) 유효성 확인
            user = serializer.validated_data["user"]
            token_creator = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_CREATOR)
            (token, _) = token_creator(user)
            return Response(token, status=status.HTTP_200_OK)



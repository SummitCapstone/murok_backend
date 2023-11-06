import logging
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drfpasswordless.serializers import CallbackTokenAuthSerializer
from drfpasswordless.settings import api_settings
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

# logger = logging.getLogger(__name__)

class ObtainJWTTokenFromCallbackToken(APIView):
    """
    Returns JWT Token(access, refresh) based on our callback token and source.
    Store refresh Token in HttpOnly Cookie.
    """
    permission_classes = (AllowAny,)
    serializer_class = CallbackTokenAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):  # 인증 코드(callback) 유효성 확인
            user = serializer.validated_data["user"]
            token_creator = import_string(api_settings.PASSWORDLESS_AUTH_TOKEN_CREATOR)
            (token, _) = token_creator(user)
            response = Response({'access_token': token['access_token']}, status=status.HTTP_200_OK)
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                key='refresh_token',
                value=token['refresh_token'],
                max_age=cookie_max_age,
                secure=False,  # https 연결에서만 쿠키 전송
                httponly=True,
                samesite='Lax'
            )
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenRefreshView(TokenRefreshView):
    """
    Refresh access Token by refresh Token.
    Refresh token is stored in HttpOnly Cookie.
    """
    def initialize_request(self, request, *args, **kwargs):
        drf_request = super().initialize_request(request, *args, **kwargs)
        drf_request.data['refresh_token'] = request.COOKIES.get('refresh')
        return drf_request

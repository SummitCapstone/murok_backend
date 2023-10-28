from django.urls import path, include
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework_simplejwt.views import (

    TokenRefreshView,
)
from .views import (ObtainJWTTokenFromCallbackToken)

urlpatterns = [
    # 'PASSWORDLESS_AUTH_PREFIX': 'auth/'
    path(api_settings.PASSWORDLESS_AUTH_PREFIX + 'email/',
         ObtainEmailCallbackToken.as_view(), name='auth_email_token'),  # Email 인증 코드 요청 (Callback Token 요청)
    path(api_settings.PASSWORDLESS_AUTH_PREFIX + 'token/',
         ObtainJWTTokenFromCallbackToken.as_view(), name='auth_jwt_token'),  # 인증 코드를 바탕으로 jwt token 요청
    path(api_settings.PASSWORDLESS_AUTH_PREFIX + 'token/refresh/',
         TokenRefreshView.as_view(), name='auth_refresh_jwt_token')  # access token refresh

]

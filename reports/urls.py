from django.urls import path, include
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework_simplejwt.views import (

    TokenRefreshView,
)

urlpatterns = [
    # 'PASSWORDLESS_AUTH_PREFIX': 'auth/'
]

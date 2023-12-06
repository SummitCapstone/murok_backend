from django.urls import path, include
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework_simplejwt.views import (

    TokenRefreshView,
)
from .views import UserReportListView, UserReportDetailView

urlpatterns = [
    path('', UserReportListView.as_view()),
    path('<str:result_id>/', UserReportDetailView.as_view()),
]

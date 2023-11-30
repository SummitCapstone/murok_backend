from django.urls import path, include
from drfpasswordless.settings import api_settings
from drfpasswordless.views import ObtainEmailCallbackToken
from rest_framework_simplejwt.views import (

    TokenRefreshView,
)
from .views import UserReportListView, UserReportDetailView

urlpatterns = [
    path('reports/', UserReportListView.as_view()),
    path('reports/<str:pk>/', UserReportDetailView.as_view()),
]

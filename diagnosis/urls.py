from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import UserRequestDiagnosis, UserRequestDiagnosisWithMQ

urlpatterns = [
    path('request/', UserRequestDiagnosisWithMQ.as_view()),
    # path('result/')
]

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import UserRequestDiagnosis

urlpatterns = [
    path('request/', UserRequestDiagnosis.as_view()),
]

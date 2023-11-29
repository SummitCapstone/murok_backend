from django.urls import path
from .views import call_api

urlpatterns = [
    path('', call_api),
]

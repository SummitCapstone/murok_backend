from django.urls import path, include

from .teapot import WhatIsThisTeapot
from .views import UserReportListView, UserReportDetailView

urlpatterns = [
    path('', UserReportListView.as_view()),
    path('<str:result_id>/', UserReportDetailView.as_view()),
    path('teapot', WhatIsThisTeapot.as_view()),
]

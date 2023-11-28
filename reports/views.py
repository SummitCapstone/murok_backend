from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from murok_backend.permissions import IsValidUser

'''
class UserReportView(APIView):
    permission_classes = (IsAuthenticated, IsValidUser)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        pass


    def delete(self, request, *args, **kwargs):

'''

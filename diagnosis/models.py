import uuid
from django.db import models
from accounts.models import User, RequestUser


class UserDiagnosisRequest(models.Model):
    id = models.UUIDField(primary_key=True,
                          editable=False)
    picture = models.ImageField(upload_to='static/uploads/blob/%Y/%m/%d/',
                                blank=False, null=False)
    crop_category = models.CharField(max_length=50,
                                     default='UNKNOWN',
                                     blank=False,
                                     null=False)
    request_date = models.DateTimeField(auto_now_add=True,
                                        editable=False)
    request_user_id = models.ForeignKey(RequestUser,
                                        on_delete=models.SET_DEFAULT,
                                        related_name='request_user_uuid',
                                        default=None)
    retry_request_id = models.ForeignKey('self', on_delete=models.SET_DEFAULT,
                                         related_name='retry_request_uuid',
                                         default=None,
                                         null=True)

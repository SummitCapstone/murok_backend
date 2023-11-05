import uuid
from django.db import models
from accounts.models import User


# All requested users including non-registered users
class DiagnosisRequestUsers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    is_registered = models.BooleanField(default=False)
    registered_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_user_id')


class UserDiagnosisRequest(models.Model):
    # Request ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requested_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_user_id')
    picture = models.ImageField(upload_to='requests/blobs/', blank=False, null=False)
    crop_category = models.CharField(max_length=50, default='UNKNOWN', blank=False)
    request_date = models.DateTimeField(auto_now_add=True)
    requester_uuid = models.ForeignKey(DiagnosisRequestUsers, on_delete=models.CASCADE,
                                       related_name='requester_uuid',
                                       null=True)

from django.db import models
from accounts.models import User, RequestUser


class UserFeedbackModel(models.Model):
    id = models.IntegerField(primary_key=True)
    # result_id = models.ForeignKey(, null=True)
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    email_address = models.EmailField(blank=False)
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


class UserPictureListModel(models.Model):
    id = models.IntegerField(primary_key=True)
    # static file
    picture = models.ImageField()
    feedback = models.ForeignKey(UserFeedbackModel,
                                 on_delete=models.CASCADE,
                                 null=True)


class AnswerFeedbackModel(models.Model):
    id = models.IntegerField(primary_key=True)
    feedback = models.ForeignKey(null=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


class AdminPictureListModel(models.Model):
    id = models.UUIDField(primary_key=True)
    # static file
    picture = models.ImageField()
    answer = models.ForeignKey(AnswerFeedbackModel,
                              on_delete=models.CASCADE,
                              null=True)

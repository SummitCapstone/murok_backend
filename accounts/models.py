from uuid import UUID, uuid4

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False)
    name = models.CharField(max_length=50, default='', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class RequestUserManager(models.Manager):

    def create_request_user(self, uuid_str: str, user: User = None):
        uuid = UUID(uuid_str)
        entity = models.Model(id=uuid, last_request_date=None, first_request_date=None, registered_user=user)

        return entity


class RequestUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    last_request_date = models.DateTimeField(auto_now=True)
    first_request_date = models.DateTimeField(auto_now_add=True, editable=False)
    registered_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_user', default=None,
                                        null=False)

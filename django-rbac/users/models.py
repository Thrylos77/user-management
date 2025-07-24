from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

# Create your models here.
class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    USER = 'USER', 'User'
    MANAGER = 'MANAGER', 'Manager'

class User(AbstractUser):
    # AbstractUser provides: id, username, first_name, last_name, email, password, etc.
    # We only need to add our custom fields.
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    history = HistoricalRecords(excluded_fields=['last_login'])

    # ['email', 'username', 'password'] by default are in REQUIRED_FIELDS from AbstractUser.
    REQUIRED_FIELDS = ['first_name', 'last_name']
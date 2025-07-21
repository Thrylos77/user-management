from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    USER = 'USER', 'User'
    MANAGER = 'MANAGER', 'Manager'

class User(AbstractUser):
    id_user = models.AutoField(primary_key=True)  # Remplace l'id de base

    lastname = models.CharField(max_length=40, null=False)
    firstname = models.CharField(max_length=120, null=False)
    username = models.CharField(max_length=60, unique=True, null=False)
    password = models.CharField(max_length=64, null=False)
    email = models.EmailField(max_length=60, null=False)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    REQUIRED_FIELDS = ['email', 'firstname', 'lastname']
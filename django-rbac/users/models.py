from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

# Create your models here.
class User(AbstractUser):
    # AbstractUser provides: id, username, first_name, last_name, email, password, etc.
    # We only need to add our custom fields.
    roles = models.ManyToManyField('rbac.Role', related_name='users', blank=True)
    history = HistoricalRecords(excluded_fields=['last_login'])
    
    # ['email', 'username', 'password'] by default are in REQUIRED_FIELDS from AbstractUser.
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def all_permissions(self):
        from rbac.models import Permission
        return Permission.objects.filter(roles__users=self).distinct()
    
    def has_permission(self, code: str) -> bool:
        return self.all_permissions.filter(code=code).exists()
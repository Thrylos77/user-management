from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
class User(AbstractUser):
    # AbstractUser provides: id, username, first_name, last_name, email, password, etc.
    # We only need to add our custom fields.
    # We override the email field to make it unique, as it's not by default in AbstractUser.
    email = models.EmailField(_('email address'), unique=True)
    roles = models.ManyToManyField('rbac.Role', related_name='users', blank=True)
    history = HistoricalRecords(excluded_fields=['last_login'])
    
    # The default REQUIRED_FIELDS for AbstractUser is ['email'].
    # We are keeping it and adding first_name and last_name. The USERNAME_FIELD ('username')
    # and password are required by default for createsuperuser.
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    @property
    def all_permissions(self):
        from rbac.models import Permission
        return Permission.objects.filter(roles__users=self).distinct()
    
    def has_permission(self, code: str) -> bool:
        return self.all_permissions.filter(code=code).exists()

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP valide pendant 10 minutes
        return (timezone.now() - self.created_at).seconds < 300 and not self.is_used
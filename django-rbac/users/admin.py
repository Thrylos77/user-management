from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from simple_history.admin import SimpleHistoryAdmin
from .logs.models import AuditLog
# Import the token models from simplejwt
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)


@admin.register(User)
class CustomUserAdmin(SimpleHistoryAdmin, UserAdmin):
    # Customize the fields displayed in the user list
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    # Add the 'role' field to the user creation and edit forms
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )

# This code registers the AuditLog model with the Django admin interface.
# It customizes the admin display for AuditLog entries:
# - Shows columns: timestamp, user, action, and details in the list view.
# - Allows filtering logs by action and user.
# - Enables searching logs by the username of the user and the details field.
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'details')
    list_filter = ('action', 'user')
    search_fields = ('user__username', 'details')

@admin.register(OutstandingToken)
class OutstandingTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'jti', 'created_at', 'expires_at')
    search_fields = ('user__username', 'jti')
    ordering = ('-created_at',)

@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'get_jti', 'blacklisted_at')
    search_fields = ('token__user__username', 'token__jti')
    ordering = ('-blacklisted_at',)

    @admin.display(description='User', ordering='token__user')
    def get_user(self, obj):
        return obj.token.user

    @admin.display(description='JTI (JWT ID)', ordering='token__jti')
    def get_jti(self, obj):
        return obj.token.jti
# This file is responsible for:
# - Validating incoming data (e.g., from forms or API requests)
# - Transforming Python/Django objects (models) to and from JSON
# - Defining the structure of data exposed or expected by the API
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .logs.models import AuditLog

# Show the User model without exposing the password field
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'role', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
       # Create a new user instance with the provided validated data.
       # The password is hashed before saving.
        user = User.objects.create_user(
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data.get('role', 'USER')
        )
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The new password must be at least 8 characters long.")
        return value

class RoleSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()

# Serializer for the historical records of the User model
class HistoricalUserSerializer(serializers.ModelSerializer):
    # The user who made the change, represented by their username for clarity.
    history_user = serializers.StringRelatedField()
    # Add a human-readable field for the history type (+, ~, -)
    history_type_display = serializers.CharField(source='get_history_type_display', read_only=True)
    changes = serializers.SerializerMethodField()

    class Meta:
        model = User.history.model
        fields = [
            'history_id',
            'history_date',
            'history_type_display',
            'history_user',
            'changes',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active'
        ]

    def get_changes(self, obj):
        if obj.history_type == '~':
            prev_record = obj.prev_record
            if not prev_record:
                return None

            delta = obj.diff_against(prev_record)
            changes_list = []
            for change in delta.changes:
                if change.field == 'date_joined':
                    continue
                # For security, we never show old or new password values.
                elif change.field == 'password':
                    changes_list.append({'field': 'password', 'old': '********', 'new': '********'})
                else:
                    changes_list.append({'field': change.field, 'old': change.old, 'new': change.new})
            return changes_list
        return None

# Serializer for the audit log entries
class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = AuditLog
        fields = ['id', 'timestamp', 'user', 'action', 'details']

# Serializer for the logout endpoint to ensure refresh token is provided
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception:
            self.fail('bad_token')

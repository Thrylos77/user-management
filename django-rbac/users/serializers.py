# This file is responsible for:
# - Validating incoming data (e.g., from forms or API requests)
# - Transforming Python/Django objects (models) to and from JSON
# - Defining the structure of data exposed or expected by the API
import json
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

from rbac.models import Role
from drf_spectacular.utils import extend_schema_field

# Show the User model without exposing the password field
class UserSerializer(serializers.ModelSerializer):
    roles = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'roles')

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Role.objects.all(),
        required=False
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'roles', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
       # Create a new user instance with the provided validated data.
       # The M2M field 'roles' must be handled after the user is created.
        roles_data = validated_data.pop('roles', [])
        user = User.objects.create_user(
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )
        # Now that the user is created, we can set the roles.
        if roles_data: # If roles were provided in the request, set them.
            user.roles.set(roles_data)
        else:
            # If no roles were provided, assign a default 'USER' role.
            try:
                default_role = Role.objects.get(name="USER")
                user.roles.add(default_role)
            except Role.DoesNotExist:
                # This handles the case where the default role might not exist yet,
                # for example in a fresh database or during tests.
                pass
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



# Serializer for the historical records of the User model
class HistoricalUserSerializer(serializers.ModelSerializer):
    # The user who made the change, represented by their username for clarity.
    history_user = serializers.StringRelatedField()
    # Add a human-readable field for the history type (+, ~, -)
    history_type_display = serializers.CharField(source='get_history_type_display', read_only=True)
    changes = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User.history.model
        fields = [
            'history_id', 'history_date', 'history_type_display',
            'history_user', 'changes', 'username', 'email',
            'first_name', 'last_name', 'roles', 'is_active'
        ]

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_roles(self, obj):
        if not obj.history_change_reason:
            return []
        try:
            data = json.loads(obj.history_change_reason)
            return data.get('roles', [])
        except (json.JSONDecodeError, TypeError):
            return []
        
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_changes(self, obj):
        if obj.history_type == '~' and obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
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
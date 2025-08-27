from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rbac.permission_control import AutoPermissionMixin
from .models import User, PasswordResetOTP
from .serializers import (
        UserSerializer, RegisterSerializer, LogoutSerializer,
        ChangePasswordSerializer, HistoricalUserSerializer,
        RequestOTPSerializer, ResetPasswordSerializer
    )
from rest_framework import status
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView
from .utils import generate_otp, send_otp_email

# Custom TokenObtainPairView to log user login
class TokenObtainPairView(SimpleJWTTokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    permission_classes = [permissions.AllowAny]
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # The user object is attached to the serializer after successful validation
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
        return response

# Register a new user
class RegisterView(AutoPermissionMixin, generics.CreateAPIView):
    serializer_class = RegisterSerializer
    resource = "user"

# This view allows users to retrieve their own details
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

# This view allows admins to list all active users
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='is_active',
            type=bool,
            location=OpenApiParameter.QUERY,
            description='Filter users by active status (true/false)'
        ),
    ]
)
class UserListView(AutoPermissionMixin, generics.ListAPIView):
    serializer_class = UserSerializer
    resource = "user"

    def get_queryset(self):
        is_active = self.request.query_params.get('is_active')
        queryset = User.objects.all().order_by('username')
        if is_active is not None:
            # Convert the string 'true' or 'false' to a boolean
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        else:
            queryset = queryset.filter(is_active=True)  # Default, only active users are shown
        return queryset


# This view allows admins to retrieve, update, or delete a user by their ID
class UserRetrieveUpdateDestroyView(AutoPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    resource = "user"

    # Destroy method is overridden to perform a soft delete
    # Instead of deleting the user, we deactivate them
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'detail': 'User has been deactivated (soft delete).'}, status=status.HTTP_204_NO_CONTENT)



# A view for logging user logout and blacklisting the refresh token
class LogoutView(AutoPermissionMixin, generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ----- Historical Read -----

class UserHistoryListView(AutoPermissionMixin, generics.ListAPIView):
    # Retrieves the change history for a specific user.
    serializer_class = HistoricalUserSerializer
    resource = "user_history"

    def get_queryset(self):
        user_pk = self.kwargs['pk']
        return User.history.filter(id=user_pk).order_by('-history_date')

@extend_schema_view(
    get=extend_schema(
        operation_id="all_user_history"
    )
)
class AllUserHistoryListView(AutoPermissionMixin, generics.ListAPIView):
    """
    Retrieves the complete change history for all users, ordered by most recent first.
    This provides a full audit trail for the system.
    """
    serializer_class = HistoricalUserSerializer
    resource = "user_history"
    queryset = User.history.all().order_by('-history_date')



# ----- Password management -----

# USER to change their own password
class ChangeOwnPasswordView(AutoPermissionMixin, generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    resource = "user"
    permission_code_map = {
        'PATCH': resource + '.change_own_password'
    }

    def get_object(self):
        return self.request.user

# For role ADMIN or Superuser to change any User password
class ChangePasswordView(AutoPermissionMixin, generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    resource = "user"
    permission_code_map = {
        'PATCH': resource + '.change_password'
    }

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return self.get_queryset().filter(pk=user_id).first()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.has_permission("user.change_password"):
            return User.objects.all()
        # Fallback None if the user don't have the permission
        return User.objects.none()

# Reset Password OTP management
class RequestOTPView(generics.CreateAPIView):
    serializer_class = RequestOTPSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.context['user']
        code = generate_otp()
        PasswordResetOTP.objects.create(user=user, code=code)
        print(f"Generated OTP: {code} for user: {user.email}")
        send_otp_email(user.email, code)

class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.context['user']
        otp_obj = serializer.context['otp_obj']
        new_password = serializer.validated_data['new_password']

        user.set_password(new_password)
        user.save()
        otp_obj.is_used = True
        otp_obj.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "✔️ Password reset successfully."}, status=status.HTTP_200_OK)
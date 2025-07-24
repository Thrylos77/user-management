from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User
from .serializers import (
        UserSerializer, RegisterSerializer, 
        ChangePasswordSerializer, RoleSerializer, LogoutSerializer,
        HistoricalUserSerializer,
    )
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from users.logs.utils import log_action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView as SimpleJWTTokenObtainPairView

# Custom TokenObtainPairView to log user login
class TokenObtainPairView(SimpleJWTTokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials. Also logs the login action.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # The user object is attached to the serializer after successful validation
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            log_action(serializer.user, 'LOGIN', 'User logged in.')
            
        return response

# Register a new user
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAdminUser]

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

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        is_active = self.request.query_params.get('is_active')
        queryset = User.objects.all()
        if is_active is not None:
            # Convert the string 'true' or 'false' to a boolean
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        else:
            queryset = queryset.filter(is_active=True)  # Default, only active users are shown
        return queryset

# This view allows admins to retrieve, update, or delete a user by their ID
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]
    # Destroy method is overridden to perform a soft delete
    # Instead of deleting the user, we deactivate them
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'detail': 'User has been deactivated (soft delete).'}, status=status.HTTP_204_NO_CONTENT)

# This view allows authenticated users to change their password
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Log the action
        log_action( 
            user=request.user,
            action='CHANGE_PASSWORD',
            details='Changed own password'
        )
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class RoleListView(generics.ListAPIView):
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, *args, **kwargs):
        from .models import Role # Import here to avoid circular dependency issues
        roles = [{'value': role.value, 'label': role.label} for role in Role.choices]
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)

class UserHistoryListView(generics.ListAPIView):
    # Retrieves the change history for a specific user.
    serializer_class = HistoricalUserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user_pk = self.kwargs['pk']
        return User.history.filter(id=user_pk).order_by('-history_date')

class AllUserHistoryListView(generics.ListAPIView):
    """
    Retrieves the complete change history for all users, ordered by most recent first.
    This provides a full audit trail for the system.
    """
    serializer_class = HistoricalUserSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.history.all().order_by('-history_date')

# A view for logging user logout and blacklisting the refresh token
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Log the action after successfully blacklisting the token
        log_action(request.user, 'LOGOUT', 'User logged out.')

        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Register a new user
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAdminUser]

# This view allows users to retrieve their own details
class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

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
            queryset = queryset.filter(is_active=True)  # Par défaut, n'affiche que les actifs
        return queryset

# This view allows admins to retrieve, update, or delete a user by their ID
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id_user'    
    permission_classes = [permissions.IsAdminUser]

    # Destroy method is overridden to perform a soft delete
    # Instead of deleting the user, we deactivate them
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'detail': 'User has been deactivated (soft delete).'}, status=status.HTTP_204_NO_CONTENT)

# This view allows authenticated users to change their password
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # The password change is always for the current user
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

# This view allows admins to list all available roles
class RoleListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from .models import Role
        roles = [{'value': role.value, 'label': role.label} for role in Role]
        return Response(roles)
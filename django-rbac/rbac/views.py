from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Role, Permission
from .serializers import ( 
        RoleSerializer, PermissionSerializer, RoleListSerializer, RoleAssignmentSerializer,
        HistoricalPermissionSerializer, HistoricalRoleSerializer,
    )
from .permission_control import HasPermission, AutoPermissionMixin
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema

User = get_user_model()

# ----- Permissions CRUD -----

class PermissionListView(AutoPermissionMixin, generics.ListAPIView):
    queryset = Permission.objects.all().order_by('code')
    serializer_class = PermissionSerializer
    resource = "permission"


class PermissionRetrieveUpdateView(AutoPermissionMixin, generics.RetrieveUpdateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    resource = "permission"

# ----- Roles CRUD -----

class RoleListCreateView(AutoPermissionMixin, generics.ListCreateAPIView):
    queryset = Role.objects.all().order_by('name')
    resource = "role"

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleSerializer
        return RoleListSerializer


class RoleRetrieveUpdateDestroyView(AutoPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.prefetch_related('permissions').all()
    serializer_class = RoleSerializer
    resource = "role"

# ----- Assignations -----

class AssignRoleToUserView(generics.CreateAPIView):
    serializer_class = RoleAssignmentSerializer
    permission_classes = [HasPermission.with_perms("rbac.assign_role")]
    queryset = User.objects.all().order_by('username')
    lookup_url_kwarg = 'user_id'

    def post(self, request, user_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_id = serializer.validated_data['role_id']

        user = self.get_object()
        role = get_object_or_404(Role, pk=role_id)

        if user.roles.filter(pk=role.pk).exists():
            return Response(
                {"detail": "This user already has the specified role."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.roles.add(role)
        return Response(
            {"detail": f"Role '{role.name}' assigned to user '{user.username}'."},
            status=status.HTTP_200_OK
        )

class RemoveRoleFromUserView(generics.GenericAPIView):
    queryset = User.objects.all().order_by('username')
    serializer_class = RoleAssignmentSerializer
    permission_classes = [HasPermission.with_perms('rbac.remove_role')]
    lookup_url_kwarg = 'user_id'

    def post(self, request, user_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_id = serializer.validated_data['role_id']

        user = self.get_object()
        role = get_object_or_404(Role, pk=role_id)

        if not user.roles.filter(pk=role.pk).exists():
            return Response(
                {"detail": "This user does not have the specified role."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.roles.remove(role)
        return Response(
            {"detail": f"Role '{role.name}' removed from user '{user.username}'."},
            status=status.HTTP_200_OK
        )




# ----- Historical Read -----
class BaseHistoryListView(generics.ListAPIView):
    """
    Base view to handle historical listing by primary key (for single object)
    or for all objects if `get_all` is set to True.
    """
    model = None  # Must be defined in subclass
    get_all = False

    def get_queryset(self):
        if self.get_all:
            return self.model.history.all().order_by('-history_date')
        obj_pk = self.kwargs['pk']
        return self.model.history.filter(id=obj_pk).order_by('-history_date')


class PermissionHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    # Retrieves the change history for a specific permission.
    serializer_class = HistoricalPermissionSerializer
    model = Permission
    resource = "permission"


@extend_schema_view(
    get=extend_schema(
        operation_id="all_permission_history"
    )
)
class AllPermissionHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    serializer_class = HistoricalPermissionSerializer
    get_all = True
    model = Permission
    resource = "permission"


class RoleHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    # Retrieves the change history for a specific role.
    serializer_class = HistoricalRoleSerializer
    model = Role
    resource = "role"

@extend_schema_view(
    get=extend_schema(
        operation_id="all_role_history"
    )
)
class AllRoleHistoryListView(AutoPermissionMixin, generics.ListAPIView):
    serializer_class = HistoricalRoleSerializer
    resource = "role"
    queryset = Role.history.all().order_by('-history_date')
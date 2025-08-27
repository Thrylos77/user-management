from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Group, Role, Permission
from .serializers import ( 
        GroupSerializer, GroupListSerializer, RoleListSerializer, 
        RoleSerializer, PermissionSerializer, RoleAssignmentSerializer, 
        HistoricalPermissionSerializer, HistoricalRoleSerializer,
        HistoricalGroupSerializer, UserGroupAssignmentSerializer,
    )
from .permission_control import AutoPermissionMixin
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

# ----- Groups CRUD -----

class GroupListCreateView(AutoPermissionMixin, generics.ListCreateAPIView):
    queryset = Group.objects.all().order_by('name')
    resource = "group"

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupSerializer
        return GroupListSerializer


class GroupRetrieveUpdateDestroyView(AutoPermissionMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.prefetch_related('permissions').all()
    serializer_class = GroupSerializer
    resource = "group"

# ----- Assign/Add & Remove -----

class BaseRoleAssignmentView(AutoPermissionMixin, generics.GenericAPIView):
    serializer_class = RoleAssignmentSerializer
    queryset = User.objects.all().order_by('username')
    lookup_url_kwarg = 'user_id'
    resource = 'rbac'
    action_type = None  # "assign" or "remove"
    permission_suffix = None  # ex: "assign_role" or "remove_role"

    def get_permission_code_map(self):
        return {'POST': f"{self.resource}.{self.permission_suffix}"}

    def post(self, request, user_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_id = serializer.validated_data['role_id']

        user = self.get_object()
        role = get_object_or_404(Role, pk=role_id)

        if self.action_type == "assign":
            if user.roles.filter(pk=role.pk).exists():
                return Response(
                    {"detail": "This user already has the specified role."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.roles.add(role)
            message = f"Role '{role.name}' assigned to user '{user.username}'."

        elif self.action_type == "remove":
            if not user.roles.filter(pk=role.pk).exists():
                return Response(
                    {"detail": "This user does not have the specified role."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.roles.remove(role)
            message = f"Role '{role.name}' removed from user '{user.username}'."

        return Response({"detail": message}, status=status.HTTP_200_OK)

class BaseUserGroupView(AutoPermissionMixin, generics.GenericAPIView):
    """
    Base class to handle adding/removing a user to/from a group.
    Subclasses define the `action` attribute as 'add' or 'remove'.
    """
    serializer_class = UserGroupAssignmentSerializer
    queryset = User.objects.all()
    lookup_url_kwarg = 'user_id'
    resource = 'rbac'
    action_type = None  # 'add' or 'remove'
    permission_suffix = None  # ex: "add_user_to_group" or "remove_user_from_group"

    def get_permission_code_map(self):
        return {'POST': f"{self.resource}.{self.permission_suffix}"}

    def post(self, request, user_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        group = get_object_or_404(Group, pk=serializer.validated_data['group_id'])

        if self.action_type == 'add':
            if group in user.groups.all():
                return Response({"detail": "User already in this group."}, status=400)
            user.groups.add(group)
            message = f"User '{user.username}' added to group '{group.name}'."
        elif self.action_type == 'remove':
            if group not in user.groups.all():
                return Response({"detail": "User is not in this group."}, status=400)
            user.groups.remove(group)
            message = f"User '{user.username}' removed from group '{group.name}'."
        else:
            return Response({"detail": "Invalid action."}, status=400)

        return Response({"detail": message}, status=200)


class AssignRoleToUserView(BaseRoleAssignmentView):
    action_type = "assign"
    permission_suffix = "assign_role"

class RemoveRoleFromUserView(BaseRoleAssignmentView):
    action_type = "remove"
    permission_suffix = "remove_role"


class AddUserToGroupView(BaseUserGroupView):
    action_type = 'add'
    permission_suffix = "add_user_to_group"

class RemoveUserFromGroupView(BaseUserGroupView):
    action_type = 'remove'
    permission_suffix = "remove_user_from_group"



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

    # Permissions
class PermissionHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    # Retrieves the change history for a specific permission.
    serializer_class = HistoricalPermissionSerializer
    model = Permission
    resource = "permission_history"


@extend_schema_view(
    get=extend_schema(
        operation_id="all_permission_history"
    )
)
class AllPermissionHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    serializer_class = HistoricalPermissionSerializer
    get_all = True
    model = Permission
    resource = "permission_history"

    # Roles
class RoleHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    # Retrieves the change history for a specific role.
    serializer_class = HistoricalRoleSerializer
    model = Role
    resource = "role_history"

@extend_schema_view(
    get=extend_schema(
        operation_id="all_role_history"
    )
)
class AllRoleHistoryListView(AutoPermissionMixin, generics.ListAPIView):
    serializer_class = HistoricalRoleSerializer
    resource = "role_history"
    queryset = Role.history.all().order_by('-history_date')

    # Groups
class GroupHistoryListView(AutoPermissionMixin, BaseHistoryListView):
    # Retrieves the change history for a specific Group.
    serializer_class = HistoricalGroupSerializer
    model = Group
    resource = "group_history"

@extend_schema_view(
    get=extend_schema(
        operation_id="all_group_history"
    )
)
class AllGroupHistoryListView(AutoPermissionMixin, generics.ListAPIView):
    serializer_class = HistoricalGroupSerializer
    resource = "group_history"
    queryset = Group.history.all().order_by('-history_date')
from django.urls import path
from .views import (
    AllPermissionHistoryListView, AllRoleHistoryListView, 
    PermissionHistoryListView, PermissionListView, 
    PermissionRetrieveUpdateView, RoleHistoryListView,
    RoleListCreateView, RoleRetrieveUpdateDestroyView,
    AssignRoleToUserView, RemoveRoleFromUserView
)

urlpatterns = [
    # Permissions
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', PermissionRetrieveUpdateView.as_view(), name='permission-ru'),
    path('permissions/history/<int:pk>/', PermissionHistoryListView.as_view(), name='permission-history-detail'),
    path('permissions/history/', AllPermissionHistoryListView.as_view(), name='permission-history-list'),
    
    # Roles
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='role-rud'),
    path('roles/history/<int:pk>/', RoleHistoryListView.as_view(), name='role-history-detail'),
    path('roles/history/', AllRoleHistoryListView.as_view(), name='role-history-list'),
    
    # Assignations
    path('roles/assign/<int:user_id>/', AssignRoleToUserView.as_view(), name='assign-role'),
    path('roles/remove/<int:user_id>/', RemoveRoleFromUserView.as_view(), name='remove-role'),    
]

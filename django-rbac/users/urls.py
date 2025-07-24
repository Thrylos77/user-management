from django.urls import path, include
from .views import (
    RegisterView, UserDetailView,
    UserListView, UserRetrieveUpdateDestroyView,
    ChangePasswordView, RoleListView, UserHistoryListView,
    AllUserHistoryListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('history/', AllUserHistoryListView.as_view(), name='all-user-history'),
    path('audit-log/', include('users.logs.urls')),
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-rud'),
    path('<int:pk>/history/', UserHistoryListView.as_view(), name='user-history'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('roles/', RoleListView.as_view(), name='role-list'),
]

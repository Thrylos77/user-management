from django.urls import path
from .views import (
    RegisterView,
    UserDetailView,
    UserListView,
    UserRetrieveUpdateDestroyView,
    ChangePasswordView,
    RoleListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('<int:id_user>/', UserRetrieveUpdateDestroyView.as_view(), name='user-rud'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('roles/', RoleListView.as_view(), name='role-list'),
]


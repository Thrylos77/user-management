from django.urls import path, include
from .views import (
    RegisterView, UserDetailView,
    UserListView, UserRetrieveUpdateDestroyView,
    ChangePasswordView, UserHistoryListView,
    AllUserHistoryListView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('', UserListView.as_view(), name='user-list'),
    path('history/', AllUserHistoryListView.as_view(), name='user-history-list'),
    path('audit-log/', include('users.logs.urls')),
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-rud'),
    path('history/<int:pk>', UserHistoryListView.as_view(), name='user-history-detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]

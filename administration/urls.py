from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    AdminParcelleListView,
    AdminParcelleDeleteView,
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='admin-user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='admin-user-detail'),
    path('parcelles/', AdminParcelleListView.as_view(), name='admin-parcelle-list'),
    path('parcelles/<int:pk>/', AdminParcelleDeleteView.as_view(), name='admin-parcelle-delete'),
]

#from rest_framework.authtoken import views as token_views
from django.urls import path
from .views import (
    LoginView, UserDashboardView, AdminDashboardView,
    AdminUserCreateView, AdminUserListView, AdminUserDetailView, 
    AdminSalleListView, AdminSalleCreateView, AdminSalleDetailView,
    AdminSalleUsersView, AdminUserSalleLinkDetailView, AdminUserSalleLinkListView,
    AdminUserSalleLinkView, AdminUserSallesView, AdminUserChangePasswordView
)

urlpatterns = [
    # Login URLS
    path('login/', LoginView.as_view(), name='login'),
    path('user-dashboard/', UserDashboardView.as_view(), name='user-dashboard'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    
    # Admin user management URLs
    path('admin-dashboard/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin-dashboard/users/create/', AdminUserCreateView.as_view(), name='admin-user-create'),
    path('admin-dashboard/users/<int:id_user>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin-dashboard/users/<int:id_user>/change-password/', AdminUserChangePasswordView.as_view(), name='admin-user-change-password'),

    # Admin salle management URLs
    path('admin-dashboard/salles/', AdminSalleListView.as_view(), name='admin-salle-list'),
    path('admin-dashboard/salles/create/', AdminSalleCreateView.as_view(), name='admin-salle-create'),
    path('admin-dashboard/salles/<int:id_salle>/', AdminSalleDetailView.as_view(), name='admin-salle-detail'),

    # Admin user-salle link management URLs
    path('admin-dashboard/links/', AdminUserSalleLinkListView.as_view(), name='admin-link-list'),
    path('admin-dashboard/links/create/', AdminUserSalleLinkView.as_view(), name='admin-link-create'),
    path('admin-dashboard/links/<int:id>/', AdminUserSalleLinkDetailView.as_view(), name='admin-link-detail'),
    
    # List Relationships views
    path('admin-dashboard/users/<int:user_id>/salles/', AdminUserSallesView.as_view(), name='admin-user-salles'),
    path('admin-dashboard/salles/<int:salle_id>/users/', AdminSalleUsersView.as_view(), name='admin-salle-users'),
]
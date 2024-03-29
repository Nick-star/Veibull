from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('create_user/', views.create_user, name='create_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('manage_users/', views.manage_users, name='manage_users'),
]

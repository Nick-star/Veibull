from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Other URL patterns
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('create_user/', views.create_user, name='create_user'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
]

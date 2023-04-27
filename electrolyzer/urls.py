from django.urls import path
from . import views

urlpatterns = [
    # Add your other URL patterns here...
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.index, name='index'),
]

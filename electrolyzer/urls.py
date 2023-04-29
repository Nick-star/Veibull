from django.urls import path
from . import views

urlpatterns = [
    # Add your other URL patterns here...
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.index, name='index'),
    path('chart/', views.chart, name='chart'),
    path('get_electrolyzer_data/', views.get_electrolyzer_data, name='get_electrolyzer_data'),
]

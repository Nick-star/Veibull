from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.index, name='index'),
    path('chart/', views.chart, name='chart'),
    path('get_electrolyzer_data/', views.get_electrolyzer_data, name='get_electrolyzer_data'),
    path('get_electrolyzer_types/', views.get_electrolyzer_types, name='get_electrolyzer_types'),
    path('get_buildings/', views.get_buildings, name='get_buildings'),
    path('tb_add/', views.tb_add, name='tb_add'),
    path('add_building/', views.add_building, name='add_building'),
    path('add_electrolyzer_type/', views.add_electrolyzer_type, name='add_electrolyzer_type'),
    path('edit-electrolyzer/<int:electrolyzer_id>/', views.edit_electrolyzer, name='edit_electrolyzer'),
    ]

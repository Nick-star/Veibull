from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.index, name='index'),
    path('chart/', views.chart, name='chart'),
    path('get_electrolyzer_data/', views.get_electrolyzer_data, name='get_electrolyzer_data'),
    path('fb_add/', views.fb_add, name='fb_add'),
    path('add_building/', views.add_building, name='add_building'),
    path('add_electrolyzer_type/', views.add_electrolyzer_type, name='add_electrolyzer_type'),
    path('add_factory/', views.add_factory, name='add_factory'),
    path('edit-electrolyzer/<int:electrolyzer_id>/', views.edit_electrolyzer, name='edit_electrolyzer'),

    path('get_factories', views.get_factories, name='get_factories'),
    path('get_buildings/', views.get_buildings, name='get_buildings'),
    path('get_part_types/', views.get_part_types, name='get_part_types'),
    path('get_oldest_date', views.get_oldest_date, name='get_oldest_date'),
    path('delete_building/', views.delete_building, name='delete_building'),
    path('update_building/<int:pk>/', views.update_building, name='update_building')
]

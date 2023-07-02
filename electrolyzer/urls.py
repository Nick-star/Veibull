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
    path('building/<int:pk>/', views.building_detail, name='building_detail'),
    path('factory/<int:factory_id>/', views.factory_details, name='factory_details'),

    path('get_factories', views.get_factories, name='get_factories'),
    path('get_buildings/', views.get_buildings, name='get_buildings'),
    path('get_part_types/', views.get_part_types, name='get_part_types'),
    path('get_oldest_date', views.get_oldest_date, name='get_oldest_date'),
    path('get_factory_buildings/<int:factory_id>/', views.get_factory_buildings, name='get_factory_buildings'),
    path('update_building/<int:building_id>/', views.update_building, name='update_building'),
    path('update_factory/<int:factory_id>/', views.update_factory, name='update_factory'),
    path('delete_factory/', views.delete_factory, name='delete_factory'),
    path('delete_building/<int:building_id>/', views.delete_building, name='delete_building'),
    path('get_building_electrolyzers/<int:building_id>/', views.get_building_electrolyzers, name='get_building_electrolyzers'),
    path('delete_electrolyzer/<int:electrolyzer_id>/', views.delete_electrolyzer, name='delete_electrolyzer'),
]

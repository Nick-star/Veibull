from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.index, name='index'),
    path('chart/', views.chart, name='chart'),
    path('fb_add/', views.fb_add, name='fb_add'),
    path('edit-electrolyzer/<int:electrolyzer_id>/', views.edit_electrolyzer, name='edit_electrolyzer'),
    path('building/<int:pk>/', views.building_detail, name='building_detail'),
    path('factory/<int:factory_id>/', views.factory_details, name='factory_details'),
    path('pt_list/', views.pt_list, name='pt_list'),
    path('part_type/<int:part_type_id>/', views.part_type_details, name='part_type_details'),


    path('add_part_type/', views.add_part_type, name='add_part_type'),
    path('add_building/', views.add_building, name='add_building'),
    path('add_electrolyzer_type/', views.add_electrolyzer_type, name='add_electrolyzer_type'),
    path('add_factory/', views.add_factory, name='add_factory'),
    path('get_factories', views.get_factories, name='get_factories'),
    path('get_electrolyzer_data/', views.get_electrolyzer_data, name='get_electrolyzer_data'),
    path('get_buildings/', views.get_buildings, name='get_buildings'),
    path('get_part_types/', views.get_part_types, name='get_part_types'),
    path('get_oldest_date', views.get_oldest_date, name='get_oldest_date'),
    path('get_factory_buildings/<int:factory_id>/', views.get_factory_buildings, name='get_factory_buildings'),
    path('get_part_type_electrolyzers/<int:part_type_id>/', views.get_part_type_electrolyzers, name='get_part_type_electrolyzers'),

    path('get_building_electrolyzers/<int:building_id>/', views.get_building_electrolyzers, name='get_building_electrolyzers'),
    path('update_building/<int:building_id>/', views.update_building, name='update_building'),
    path('update_factory/<int:factory_id>/', views.update_factory, name='update_factory'),
    path('update_part_type/<int:part_type_id>/', views.update_part_type, name='update_part_type'),
    path('delete_factory/', views.delete_factory, name='delete_factory'),
    path('delete_building/<int:building_id>/', views.delete_building, name='delete_building'),
    path('delete_electrolyzer/<int:electrolyzer_id>/', views.delete_electrolyzer, name='delete_electrolyzer'),
    path('delete_part_type/<int:part_type_id>/', views.delete_part_type, name='delete_part_type'),
]

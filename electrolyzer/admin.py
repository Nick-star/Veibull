from django.contrib import admin
from .models import Electrolyzer, ElectrolyzerType, Building

admin.site.register(Electrolyzer)
admin.site.register(ElectrolyzerType)
admin.site.register(Building)

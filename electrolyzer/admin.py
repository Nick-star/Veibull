from django.contrib import admin
from .models import PartType, Part, History, Factory, Building, Electrolyzer


class HistoryInline(admin.TabularInline):
    readonly_fields = ('days',)
    model = History
    extra = 0


class PartAdmin(admin.ModelAdmin):
    readonly_fields = ('avg_days',)
    inlines = [HistoryInline]


class BuildingInline(admin.TabularInline):
    model = Building
    extra = 0


class FactoryAdmin(admin.ModelAdmin):
    inlines = [BuildingInline]


admin.site.register(PartType)
admin.site.register(Part, PartAdmin)
admin.site.register(Factory, FactoryAdmin)
admin.site.register(Electrolyzer)

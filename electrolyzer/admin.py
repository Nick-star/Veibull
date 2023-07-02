from django.contrib import admin
from .models import PartType, Part, History, Factory, Building


class HistoryInline(admin.TabularInline):
    readonly_fields = ('days',)
    model = History
    extra = 0


class PartAdmin(admin.ModelAdmin):
    list_display = ('number', 'part_type', 'building')
    search_fields = ['number', 'part_type__id', 'building__id']
    readonly_fields = ('avg_days',)
    inlines = [HistoryInline]


class BuildingInline(admin.TabularInline):
    model = Building
    extra = 0


class FactoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [BuildingInline]


admin.site.register(PartType)
admin.site.register(Part, PartAdmin)
admin.site.register(Factory, FactoryAdmin)

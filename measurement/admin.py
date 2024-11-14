
from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from measurement.models import ValueType, Value, Measurement


@admin.register(ValueType)
class ValueTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'slug', 'unit', 'sort_order']
    search_fields = ['name']


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ['date', 'comment', 'owner']
    list_filter = ['owner']
    date_hierarchy = 'date'


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ['value_type', 'value', 'measurement']
    list_filter = ['value_type', 'measurement__owner']
    date_hierarchy = 'measurement__date'
    autocomplete_fields = ['value_type']

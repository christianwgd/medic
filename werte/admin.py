# -*- coding: utf-8 -*-
from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from werte.models import Wert, ValueType, Value, Measurement


@admin.register(ValueType)
class ValueTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'slug', 'unit', 'owner', 'sort_order']
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


@admin.register(Wert)
class WertAdmin(admin.ModelAdmin):
    list_display = ['date', 'rrsys', 'rrdia', 'puls', 'temp', 'gew']
    list_filter = ['ref_usr']

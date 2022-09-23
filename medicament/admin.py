# -*- coding: utf-8 -*-
from django.contrib import admin

from medicament.models import Medicament, StockChange


@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):

    list_display = ['name', 'strength', 'unit', 'package']
    list_filter = ['owner']
    search_fields = ['name']


@admin.register(StockChange)
class StockChangeAdmin(admin.ModelAdmin):

    list_display = ['medicament', 'amount', 'date', 'reason']
    list_filter = ['medicament', 'owner']
    date_hierarchy = 'date'

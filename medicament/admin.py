
from django.contrib import admin

from medicament.models import Medicament, StockChange, DosageForm, MedPznData


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


@admin.register(DosageForm)
class DosageFormAdmin(admin.ModelAdmin):

    list_display = ['key', 'short', 'name']
    search_fields = ['key', 'short', 'name']


@admin.register(MedPznData)
class MedPznDataAdmin(admin.ModelAdmin):

    list_display = ['pzn', 'name', 'producer']
    search_fields = ['pzn', 'name']

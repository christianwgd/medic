from django.contrib import admin
from django.utils.translation import gettext as _

from prescription.models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin (admin.ModelAdmin):

    list_display = ['medicament', 'morning', 'noon', 'evening', 'night', 'mo', 'tu', 'we', 'th', 'fr', 'sa', 'so']
    list_filter = ['owner']
    search_fields = ['medicament__name']
    autocomplete_fields = ['medicament', 'owner']
    date_hierarchy = 'valid_from'
    fieldsets = (
        (_('User'),
            {'fields': (('owner',),)}),
        (_('Medicament'),
            {'fields': (('medicament',),)}),
        (_('Dosage'), {
            'fields': (('morning', 'noon', 'evening', 'night'), ('mo', 'tu', 'we', 'th', 'fr', 'sa', 'so'))
        }),
        (_('Valid'), {
            'fields': (('valid_from', 'valid_until'),)
        }),
    )

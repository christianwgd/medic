# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from medikamente.models import Medikament, Verordnung, Bestandsveraenderung


class MedikamentAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'staerke', 'einheit', 'packung', 'bestand', 'bestand_vom']
    list_filter = ['ref_usr']


class VerordnungAdmin (admin.ModelAdmin):
    
    list_display = ['ref_medikament', 'morgen', 'mittag', 'abend', 'nacht', 'mo', 'di', 'mi', 'do', 'fr', 'sa', 'so']
    list_filter = ['ref_usr']
    fieldsets = (
        (_('User'),
            {'fields': (('ref_usr',),)}),
        (_('Medicine'),
            {'fields': (('ref_medikament',),)}),
        (_('Dosage'), {
            'fields': (('morgen', 'mittag', 'abend', 'nacht'), ('mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'))
        }),
    )


class BestandsveraenderungAdmin (admin.ModelAdmin):
    
    list_display = ['ref_medikament', 'menge', 'grund', 'text']
    list_filter = ['ref_medikament', 'ref_usr']


admin.site.register(Medikament, MedikamentAdmin)
admin.site.register(Verordnung, VerordnungAdmin)
admin.site.register(Bestandsveraenderung, BestandsveraenderungAdmin)

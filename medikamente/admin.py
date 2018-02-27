# -*- coding: utf-8 -*-

from django.contrib import admin
from medikamente.models import Medikament, Verordnung, Bestandsveraenderung


class MedikamentAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'staerke', 'einheit', 'packung', 'bestand', 'bestand_vom']
    list_filter = ['ref_usr']


class VerordnungAdmin (admin.ModelAdmin):
    
    list_display = ['ref_medikament', 'morgen', 'mittag', 'abend', 'nacht', 'mo', 'di', 'mi', 'do', 'fr', 'sa', 'so']
    list_filter = ['ref_usr']
    fieldsets = (
        ('Verbindung',
            {'fields': (('ref_usr', 'ref_medikament'),)}),
        ('Dosierung', {
            'fields': (('morgen', 'mittag', 'abend', 'nacht'), ('mo', 'di', 'mi', 'do', 'fr', 'sa', 'so'))
        }),
    )


class BestandsveraenderungAdmin (admin.ModelAdmin):
    
    list_display = ['ref_medikament', 'menge', 'grund', 'text']
    list_filter = ['ref_medikament', 'ref_usr']


admin.site.register(Medikament, MedikamentAdmin)
admin.site.register(Verordnung, VerordnungAdmin)
admin.site.register(Bestandsveraenderung, BestandsveraenderungAdmin)

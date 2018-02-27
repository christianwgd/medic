# -*- coding: utf-8 -*-

from django.contrib import admin
from werte.models import Wert


class WertAdmin(admin.ModelAdmin):
    
    list_display = ['date', 'rrsys', 'rrdia', 'puls', 'temp', 'gew']
    list_filter = ['ref_usr']
    
    
admin.site.register(Wert, WertAdmin)

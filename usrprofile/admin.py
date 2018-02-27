# -*- coding: utf-8 -*-

from django.contrib import admin
from orderable.admin import OrderableAdmin

from usrprofile.models import UserProfile, StartUrl


class UserProfileAdmin(admin.ModelAdmin):
    
    list_display = ['ref_usr', 'warnenTageVorher', 'werteLetzteTage']
    list_filter = ['ref_usr']


class StartUrlAdmin(OrderableAdmin):

    list_display = ['name', 'sort_order_display']
    ordering = ['sort_order']
    exclude = ('sort_order',)

    
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(StartUrl, StartUrlAdmin)

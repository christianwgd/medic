# -*- coding: utf-8 -*-
from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from usrprofile.models import UserProfile, StartUrl


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ['ref_usr', 'warn_days_before', 'show_measurement_days']
    list_filter = ['ref_usr']


@admin.register(StartUrl)
class StartUrlAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ['name']
    ordering = ['sort_order']
    exclude = ('sort_order',)

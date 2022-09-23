from django.contrib import admin

from order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = ['date', 'owner', 'done']
    list_filter = ['owner']
    date_hierarchy = 'date'
    autocomplete_fields = ['medicaments']

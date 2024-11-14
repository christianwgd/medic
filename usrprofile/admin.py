
from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext_lazy as _

from usrprofile.models import UserProfile, StartUrl


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ['ref_usr', 'warn_days_before', 'show_measurement_days']
    list_filter = ['ref_usr']
    autocomplete_fields = ['active_value_types']


class StartUrlAdminForm(forms.ModelForm):

    class Meta:
        model = StartUrl
        fields = ['name', 'url']

    def clean_url(self):
        url_name = self.cleaned_data['url']
        try:
            reverse(url_name)
        except NoReverseMatch as exc:
            raise ValidationError(_("Not a valid url name")) from exc
        return url_name


@admin.register(StartUrl)
class StartUrlAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ['name']
    ordering = ['sort_order']
    exclude = ('sort_order',)
    form = StartUrlAdminForm

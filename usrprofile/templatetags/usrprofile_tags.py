# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _
from django import template

from usrprofile.models import UserProfile


register = template.Library()


@register.inclusion_tag('usrprofile/includes/userheader.html')
def user_header(title, user, name=None):
    try:
        user_profile = UserProfile.objects.get(ref_usr=user)
        user_info = user_profile.usr_inf
    except UserProfile.DoesNotExist:
        user_info = _('unknown')
    return {'userinfo': user_info, 'title': title, 'name': name}

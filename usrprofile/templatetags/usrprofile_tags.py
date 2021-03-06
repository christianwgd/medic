# -*- coding: utf-8 -*-
from django.utils.translation import gettext_lazy as _
from django import template

from usrprofile.models import UserProfile


register = template.Library()


@register.inclusion_tag('usrprofile/includes/userheader.html')
def user_header(title, user, *args, **kwargs):
    try:
        userprof = UserProfile.objects.get(ref_usr=user)
        userinfo = userprof.usrinf
    except Exception as e:
        userinfo = _('unknown')
    return {'userinfo': userinfo, 'title': title}
    
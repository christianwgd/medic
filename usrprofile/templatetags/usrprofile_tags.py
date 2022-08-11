# -*- coding: utf-8 -*-
from django import template


register = template.Library()


@register.inclusion_tag('usrprofile/includes/userheader.html')
def user_header(title, user, name=None):
    return {'userinfo': user.profile.usr_inf, 'title': title, 'name': name}

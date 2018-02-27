# encoding: utf-8

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages.constants import ERROR
from django.contrib.auth.decorators import login_required

from logging import getLogger

from usrprofile.models import UserProfile

logger = getLogger('medic')


# Aufruf der Hauptnavigation
@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html', {})


@login_required(login_url='/login/')
def startpage(request):
    try:
        usr = User.objects.get(username=request.user.username)
        usrProf = UserProfile.objects.get(ref_usr=usr)
        if usrProf.myStartPage:
            startpage = usrProf.myStartPage.url
        else:
            startpage = 'index'
        return HttpResponseRedirect(reverse_lazy(startpage))
    except User.DoesNotExist:
        message = 'Benutzer existiert nicht.'
        messages.add_message(request, ERROR, message)
        return HttpResponseRedirect(reverse_lazy('startpage'))
    except UserProfile.DoesNotExist:
        message = 'Der Benutzer {} hat kein Benutzerprofil.'.format(usr)
        messages.add_message(request, ERROR, message)
        return HttpResponseRedirect(reverse_lazy('usrprofile:userprof'))


def is_ascii(s):
    try:
        s.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True


def log_off(request):
    user = request.user.username
    try:
        logout(request)
        logger.info('User %s logged out' % user)
    except Exception as e:
        logger.exception('Fehler beim Logoff (User: %s)! (%s)' % (user, e))
    return HttpResponseRedirect(reverse_lazy('kas_login'))

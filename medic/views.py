# encoding: utf-8
from logging import getLogger

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from usrprofile.models import UserProfile

logger = getLogger('medic')
User = auth.get_user_model()


# Aufruf der Hauptnavigation
@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html', {})


@login_required(login_url='/login/')
def startpage(request):
    try:
        # messages.info(request, 'info with a little more text text text text')
        # messages.success(request, 'success')
        # messages.warning(request, 'warning')
        # messages.error(request, 'error')
        usr = User.objects.get(username=request.user.username)
        profile = UserProfile.objects.get(ref_usr=usr)
        if profile.myStartPage:
            start_page = profile.myStartPage.url
        else:
            start_page = 'index'
        return redirect(reverse_lazy(start_page))
    except User.DoesNotExist:
        message = _('User does not exist.')
        messages.error(request, message)
        return redirect(reverse_lazy('startpage'))
    except UserProfile.DoesNotExist:
        message = _(f'User {usr} has no user profile.')
        messages.error(request, message)
        return redirect(reverse_lazy('usrprofile:userprof'))


def log_off(request):
    logout(request)
    return redirect(reverse_lazy('medic_login'))

# encoding: utf-8
from logging import getLogger

from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


logger = getLogger('medic')
User = auth.get_user_model()


# Aufruf der Hauptnavigation
@login_required(login_url='/accounts/login/')
def index(request):
    return render(request, 'index.html', {})


@login_required(login_url='/accounts/login/')
def startpage(request):
    profile = request.user.profile
    if profile.my_start_page:
        start_page = profile.my_start_page.url
    else:
        start_page = 'index'
    return redirect(reverse_lazy(start_page))


def log_off(request):
    logout(request)
    return redirect(reverse_lazy('medic_login'))

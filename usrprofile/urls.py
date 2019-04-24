from django.urls import path

from . import  views

app_name = 'usrprofile'
urlpatterns = [
    path('userprof/', views.userprof, name='userprof'),
]
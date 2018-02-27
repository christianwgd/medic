from django.conf.urls import url

from . import  views

app_name = 'usrprofile'
urlpatterns = [
    url(r'^userprof/', views.userprof, name='userprof'),
]
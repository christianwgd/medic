from django.urls import path

from . import  views

app_name = 'usrprofile'
urlpatterns = [
    path('userprof/', views.UserProfileUpdateView.as_view(), name='userprof'),
]

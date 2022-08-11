from django.urls import path

from . import  views

app_name = 'usrprofile'
urlpatterns = [
    path('update/', views.UserProfileUpdateView.as_view(), name='update'),
]

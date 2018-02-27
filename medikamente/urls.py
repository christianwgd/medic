from django.conf.urls import url

from . import  views

app_name = 'medikamente'
urlpatterns = [
    url(r'^medikamente/$', views.medikamente, name='medikamente'),
    url(r'^mededit/(?P<med_id>\d+)/$', views.mededit, name='mededit'),
    url(r'^mednew/$', views.mednew, name='mednew'),
    url(r'^getmed/(?P<med_id>\d+)/$', views.getmed, name='getmed'),
    url(r'^deletemed/(?P<pk>\d+)/$', views.MedDelete.as_view(), name='deletemed'),

    url(r'^verordnungen/$', views.verordnungen, name='verordnungen'),
    url(r'^mailvrd/$', views.emailverordnungen, name='emailverordnungen'),
    url(r'^vrdedit/(?P<vrd_id>\d+)/$', views.vrdedit, name='vrdedit'),
    url(r'^vrdnew/$', views.vrdnew, name='vrdnew'),
    url(r'^deletevrd/(?P<pk>[0-9]+)/$', views.VerordnungDelete.as_view(), name='deletevrd'),

    url(r'^vrdfutchange/$', views.vrdfutchange, name='vrdfutchange'),
    url(r'^vrdfutnew/$', views.vrdfutnew, name='vrdfutedit'),
    url(r'^vrdfutedit/(?P<vrdfut_id>\d+)/$', views.vrdfutedit, name='vrdfutedit'),
    url(r'^vrdfuthistory/$', views.vrdfuthistory, name='vrdfuthistory'),

    url(r'^bestandedit/(?P<med_id>\d+)/$', views.bestandedit, name='bestandedit'),
    url(r'^besthistory/(?P<med_id>\d+)/$', views.besthistory, name='besthistory'),
]

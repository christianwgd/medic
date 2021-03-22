from django.urls import path

from . import  views

app_name = 'medikamente'

urlpatterns = [
    path('medikamente/', views.MedListView.as_view(), name='medikamente'),
    path('mededit/<int:pk>/', views.MedUpdateView.as_view(), name='mededit'),
    path('mednew/', views.MedCreateView.as_view(), name='mednew'),
    path('getmed/(<int:med_id>/', views.getmed, name='getmed'),
    path('deletemed/<int:pk>/', views.MedDeleteView.as_view(), name='deletemed'),

    path('verordnungen/', views.verordnungen, name='verordnungen'),
    path('mailvrd/', views.emailverordnungen, name='emailverordnungen'),
    path('vrdedit/<int:vrd_id>/', views.vrdedit, name='vrdedit'),
    path('vrdnew/', views.vrdnew, name='vrdnew'),
    path('deletevrd/<int:pk>/', views.VerordnungDelete.as_view(), name='deletevrd'),

    path('vrdfutchange/', views.vrdfutchange, name='vrdfutchange'),
    path('vrdfutnew/', views.vrdfutnew, name='vrdfutedit'),
    path('vrdfutedit/<int:vrdfut_id>/', views.vrdfutedit, name='vrdfutedit'),
    path('vrdfuthistory/', views.vrdfuthistory, name='vrdfuthistory'),

    path('bestandedit/<int:med_id>/', views.bestandedit, name='bestandedit'),
    path('besthistory/<int:med_id>/', views.besthistory, name='besthistory'),
]

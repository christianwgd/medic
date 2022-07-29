from django.urls import path

from . import  views

app_name = 'medicament'

urlpatterns = [
    path('list/', views.MedicamentListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.MedicamentDetailView.as_view(), name='detail'),
    path('create/', views.MedicamentCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.MedicamentUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.MedicamentDeleteView.as_view(), name='delete'),
    path('get/<int:med_id>/', views.getmed, name='get'),
]

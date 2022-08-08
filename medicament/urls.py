from django.urls import path

from . import  views

app_name = 'medicament'

urlpatterns = [
    path('list/', views.MedicamentListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.MedicamentDetailView.as_view(), name='detail'),
    path('create/', views.MedicamentCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.MedicamentUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.MedicamentDeleteView.as_view(), name='delete'),
    path('stock-change/<int:med_id>/', views.StockChangeCreateView.as_view(), name='stock-change'),
    path('stock-history/<int:med_id>/', views.StockChangeHistoryView.as_view(), name='stock-history'),
    path('stock-calc/<int:med_id>/', views.calc_consumption, name='stock-calc'),
]

from django.urls import path

from prescription import views

app_name = 'prescription'

urlpatterns = [
    path('list/', views.PrescriptionListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.PrescriptionDetailView.as_view(), name='detail'),
    path('create/', views.PrescriptionCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.PrescriptionUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.PrescriptionDeleteView.as_view(), name='delete'),
    # path('print/', views.PrescriptionPrintView.as_view(), name='print'),
]

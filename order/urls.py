from django.urls import path

from . import views

app_name = 'order'


urlpatterns = [
    path('list/', views.OrderListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.OrderUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', views.OrderDeleteView.as_view(), name='delete'),
    path('close/<int:order_id>/', views.close_order, name='close'),
]

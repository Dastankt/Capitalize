from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('add/', views.transaction_add, name='transaction_add'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('<int:pk>/confirm/', views.transaction_confirm, name='transaction_confirm'),
    path('<int:pk>/cancel/', views.transaction_cancel, name='transaction_cancel'),
]
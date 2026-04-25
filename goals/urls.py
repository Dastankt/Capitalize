from django.urls import path
from . import views

urlpatterns = [
    path('', views.goal_list, name='goal_list'),
    path('add/', views.goal_add, name='goal_add'),
    path('<int:pk>/contribute/', views.goal_contribute, name='goal_contribute'),
    path('<int:pk>/delete/', views.goal_delete, name='goal_delete'),
]
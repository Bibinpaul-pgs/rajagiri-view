from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.room_list, name='room_list'),
    path('<int:room_id>/', views.room_retrieve, name='room_retrieve'),
    path('create/', views.room_create, name='room_create'),
    path('<int:room_id>/update/', views.room_update, name='room_update'),
    path('<int:room_id>/delete/', views.room_delete, name='room_delete'),
]

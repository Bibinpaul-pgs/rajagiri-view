from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),

    # Guest endpoints
    # path('guest/register/', views.guest_register, name='guest_register'),
    # path('guest/list/', views.guest_list, name='guest_list'),
    path('guest/list-stats/', views.guest_list_with_stats, name='guest_list_with_stats'),
    # path('guest/<int:guest_id>/', views.guest_retrieve, name='guest_retrieve'),
    path('guest/<str:guest_email>/details/', views.guest_detail_with_bookings, name='guest_detail_with_bookings'),
]


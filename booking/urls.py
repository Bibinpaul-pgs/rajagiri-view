from django.urls import path
from .views import booking_list, booking_retrieve, booking_create, booking_update, booking_delete, booking_grouped_by_date, booking_analytics

urlpatterns = [
    path('list/', booking_list, name='booking_list'),
    path('grouped-by-date/', booking_grouped_by_date, name='booking_grouped_by_date'),
    path('analytics/', booking_analytics, name='booking_analytics'),
    path('<int:booking_id>/', booking_retrieve, name='booking_retrieve'),
    path('create/', booking_create, name='booking_create'),
    path('<int:booking_id>/update/', booking_update, name='booking_update'),
    path('<int:booking_id>/delete/', booking_delete, name='booking_delete'),
]

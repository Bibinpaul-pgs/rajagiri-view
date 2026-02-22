from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'name', 'type', 'price', 'capacity', 'is_available']
    list_filter = ['type', 'is_available', 'capacity']
    search_fields = ['number', 'name', 'address']
    readonly_fields = ['id']
    fieldsets = (
        ('Room Information', {
            'fields': ('id', 'number', 'name', 'description', 'type')
        }),
        ('Details', {
            'fields': ('price', 'address', 'capacity', 'is_available')
        }),
    )

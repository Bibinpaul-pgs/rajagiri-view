from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest_name', 'room', 'check_in_date', 'check_out_date', 'booking_platform', 'total_amount', 'created_at']
    list_filter = ['booking_platform', 'check_in_date', 'check_out_date', 'created_at']
    search_fields = ['guest_name', 'guest_email', 'guest_phone_number', 'room__number', 'room__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Guest Information', {
            'fields': ('guest_name', 'guest_phone_number', 'guest_email', 'guest_address')
        }),
        ('ID Proof', {
            'fields': ('guest_id_proof_type', 'guest_id_proof_number')
        }),
        ('Room & Platform', {
            'fields': ('room', 'booking_platform')
        }),
        ('Check-in Details', {
            'fields': ('check_in_date', 'check_in_time')
        }),
        ('Check-out Details', {
            'fields': ('check_out_date', 'check_out_time')
        }),
        ('Guest Count', {
            'fields': ('adults', 'children')
        }),
        ('Payment Information', {
            'fields': ('total_amount', 'advance_amount', 'pending_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

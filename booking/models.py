from django.db import models
from user.models import Guest
from room.models import Room

class Booking(models.Model):
    PLATFORM_CHOICES = [
        ('walk_in', 'Walk-in'),
        ('airbnb', 'Airbnb'),
    ]

    BOOKING_STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    guest_name = models.CharField(max_length=100)
    guest_phone_number = models.CharField(max_length=20)
    guest_email = models.EmailField(unique=False)
    guest_address = models.CharField(max_length=255, null=True, blank=True)
    guest_id_proof_type = models.CharField(max_length=50)
    guest_id_proof_number = models.CharField(max_length=100)
    check_in_date = models.DateField()
    check_in_time = models.TimeField()
    check_out_date = models.DateField()
    check_out_time = models.TimeField()
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    booking_platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='walk_in')
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='booked')
    # Payment Details
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    #additional information
    reference = models.CharField(max_length=255, null=True, blank=True)
    special_requests = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking {self.id} - {self.guest_name} - {self.room.number}"
    
    class Meta:
        ordering = ['-created_at']

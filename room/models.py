from django.db import models

# Create your models here.
class Room(models.Model):
    type_choices = [
        ('Room', 'Room'),
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('PG', 'PG'),
    ]
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=type_choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)

    def __str__(self):
        return f"Room {self.number} - {self.type}"


class RoomPricing(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='custom_pricing')
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"Room {self.room.number} | {self.start_date} – {self.end_date} | ₹{self.price}"
from django.db import models

# Create your models here.
class Room(models.Model):
    type_choices = [
        ('room', 'Room'),
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('pg', 'PG'),
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
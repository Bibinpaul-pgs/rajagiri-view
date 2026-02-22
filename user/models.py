from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    role = models.CharField(max_length=50, default='user')
    
    class Meta:
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.get_full_name() or self.username


class Guest(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    address = models.TextField()
    id_proof_type = models.CharField(max_length=50)
    id_proof_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
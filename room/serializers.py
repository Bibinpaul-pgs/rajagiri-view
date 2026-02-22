from rest_framework import serializers
from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model"""
    
    class Meta:
        model = Room
        fields = ['id', 'number', 'name', 'description', 'type', 'price', 'address', 'capacity', 'is_available', 'image']
        read_only_fields = ['id']
        extra_kwargs = {
            'number': {'help_text': 'Unique room number'},
            'name': {'help_text': 'Room name'},
            'description': {'help_text': 'Room description'},
            'type': {'help_text': 'Room type (room, house, apartment, pg)'},
            'price': {'help_text': 'Price per month'},
            'address': {'help_text': 'Room address'},
            'capacity': {'help_text': 'Maximum occupancy'},
            'is_available': {'help_text': 'Is room available for booking'},
            'image': {'help_text': 'Room image file (JPEG, PNG, etc.)', 'required': False, 'allow_null': True},
        }

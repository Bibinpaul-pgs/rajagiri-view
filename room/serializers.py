from rest_framework import serializers
from .models import Room, RoomPricing


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'number', 'name', 'description', 'type', 'price', 'address', 'capacity', 'is_available', 'image', 'image_url']
        read_only_fields = ['id', 'image_url']
        extra_kwargs = {
            'number': {'help_text': 'Unique room number'},
            'name': {'help_text': 'Room name'},
            'description': {'help_text': 'Room description'},
            'type': {'help_text': 'Room type (room, house, apartment, pg)'},
            'price': {'help_text': 'Price per month'},
            'address': {'help_text': 'Room address'},
            'capacity': {'help_text': 'Maximum occupancy'},
            'is_available': {'help_text': 'Is room available for booking'},
            'image': {'help_text': 'Room image file (JPEG, PNG, etc.)', 'required': False, 'allow_null': True, 'write_only': True},
        }

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class RoomPricingSerializer(serializers.ModelSerializer):
    """Serializer for custom room pricing by date range"""

    class Meta:
        model = RoomPricing
        fields = ['id', 'room', 'start_date', 'end_date', 'price', 'reason', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'room': {'help_text': 'Room ID'},
            'start_date': {'help_text': 'Start date of the custom price (YYYY-MM-DD)'},
            'end_date': {'help_text': 'End date of the custom price (YYYY-MM-DD)'},
            'price': {'help_text': 'Custom price for this date range'},
            'reason': {'help_text': 'Reason for price change (e.g. holiday, peak season)', 'required': False},
        }

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end and start > end:
            raise serializers.ValidationError({'end_date': 'end_date must be on or after start_date.'})
        return data

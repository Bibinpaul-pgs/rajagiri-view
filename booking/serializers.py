from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Booking
from room.serializers import RoomSerializer


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    room = RoomSerializer(read_only=True)
    room_id = serializers.IntegerField(write_only=True)
    nights = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'room',
            'room_id',
            'guest_name',
            'guest_phone_number',
            'guest_email',
            'guest_address',
            'guest_id_proof_type',
            'guest_id_proof_number',
            'check_in_date',
            'check_in_time',
            'check_out_date',
            'check_out_time',
            'nights',
            'adults',
            'children',
            'booking_platform',
            'booking_status',
            'total_amount',
            'advance_amount',
            'pending_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'guest_name': {'help_text': 'Guest name'},
            'guest_phone_number': {'help_text': 'Guest phone number'},
            'guest_email': {'help_text': 'Guest email address'},
            'guest_address': {'help_text': 'Guest address'},
            'guest_id_proof_type': {'help_text': 'Type of ID proof (Passport, Aadhar, PAN, etc.)'},
            'guest_id_proof_number': {'help_text': 'ID proof number'},
            'check_in_date': {'help_text': 'Check-in date (YYYY-MM-DD)'},
            'check_in_time': {'help_text': 'Check-in time (HH:MM:SS)'},
            'check_out_date': {'help_text': 'Check-out date (YYYY-MM-DD)'},
            'check_out_time': {'help_text': 'Check-out time (HH:MM:SS)'},
            'booking_platform': {'help_text': 'Booking platform (walk_in or airbnb)'},
            'total_amount': {'help_text': 'Total booking amount'},
            'advance_amount': {'help_text': 'Advance payment'},
            'pending_amount': {'help_text': 'Pending payment'},
            'booking_status': {'help_text': 'Booking status (booked, checked_in, checked_out, cancelled)'},
        }
    
    def create(self, validated_data):
        room_id = validated_data.pop('room_id')
        from room.models import Room
        
        room = Room.objects.get(id=room_id)
        booking = Booking.objects.create(room=room, **validated_data)
        return booking
    
    def update(self, instance, validated_data):
        if 'room_id' in validated_data:
            room_id = validated_data.pop('room_id')
            from room.models import Room
            instance.room = Room.objects.get(id=room_id)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    @extend_schema_field(serializers.IntegerField())
    def get_nights(self, obj) -> int:
        """Calculate number of nights between check-out and check-in dates"""
        if obj.check_in_date and obj.check_out_date:
            return (obj.check_out_date - obj.check_in_date).days
        return 0

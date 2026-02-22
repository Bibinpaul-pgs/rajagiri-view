from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import User, Guest


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - returns user profile data"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Password must be at least 6 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Confirm password must match the password field"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'role']
        extra_kwargs = {
            'username': {'help_text': 'Username for login'},
            'email': {'help_text': 'Unique email address for the user'},
            'first_name': {'help_text': 'First name of the user'},
            'last_name': {'help_text': 'Last name of the user'},
            'role': {'help_text': 'User role (e.g., user, admin, moderator)'},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(help_text="User email address")
    password = serializers.CharField(
        write_only=True,
        help_text="User password"
    )


class GuestSerializer(serializers.ModelSerializer):
    """Serializer for Guest model"""
    class Meta:
        model = Guest
        fields = ['id', 'name', 'phone_number', 'email', 'address', 'id_proof_type', 'id_proof_number', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'help_text': 'Guest name'},
            'phone_number': {'help_text': 'Guest phone number'},
            'email': {'help_text': 'Guest email address'},
            'address': {'help_text': 'Guest address'},
            'id_proof_type': {'help_text': 'Type of ID proof (e.g., PAN, Aadhaar, Passport)'},
            'id_proof_number': {'help_text': 'ID proof number'},
        }

class GuestDetailedSerializer(serializers.Serializer):
    """Serializer for Guest details extracted from bookings with statistics"""
    id = serializers.SerializerMethodField()
    name = serializers.CharField()
    phone_number = serializers.CharField()
    email = serializers.CharField()
    address = serializers.CharField()
    id_proof_type = serializers.CharField()
    id_proof_number = serializers.CharField()
    total_bookings = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    total_nights = serializers.SerializerMethodField()
    total_guests_count = serializers.SerializerMethodField()
    last_booking_date = serializers.SerializerMethodField()
    booking_platforms = serializers.SerializerMethodField()
    booking_history = serializers.SerializerMethodField()
    
    @extend_schema_field(serializers.IntegerField())
    def get_id(self, obj) -> int:
        """Get unique ID based on email"""
        return hash(obj['email']) % 100000
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_bookings(self, obj) -> int:
        """Get total number of bookings for this guest"""
        from booking.models import Booking
        return Booking.objects.filter(guest_email=obj['email']).count()
    
    @extend_schema_field(serializers.FloatField())
    def get_total_revenue(self, obj) -> float:
        """Get total revenue from all bookings"""
        from booking.models import Booking
        bookings = Booking.objects.filter(guest_email=obj['email'])
        return sum(float(booking.total_amount) for booking in bookings)
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_nights(self, obj) -> int:
        """Calculate total number of nights booked"""
        from booking.models import Booking
        bookings = Booking.objects.filter(guest_email=obj['email'])
        total_nights = 0
        for booking in bookings:
            nights = (booking.check_out_date - booking.check_in_date).days
            total_nights += nights
        return total_nights
    
    @extend_schema_field(serializers.IntegerField())
    def get_total_guests_count(self, obj) -> int:
        """Get total count of adults and children across all bookings"""
        from booking.models import Booking
        bookings = Booking.objects.filter(guest_email=obj['email'])
        total = 0
        for booking in bookings:
            total += booking.adults + booking.children
        return total
    
    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_last_booking_date(self, obj) -> str:
        """Get the most recent booking check-in date for this guest"""
        from booking.models import Booking
        booking = Booking.objects.filter(guest_email=obj['email']).order_by('-check_in_date').first()
        if booking:
            return booking.check_in_date.strftime('%Y-%m-%d')
        return None
    
    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_booking_platforms(self, obj) -> list:
        """Get list of unique booking platforms used by this guest"""
        from booking.models import Booking
        bookings = Booking.objects.filter(guest_email=obj['email'])
        platforms = list(set([booking.booking_platform for booking in bookings if booking.booking_platform]))
        return sorted(platforms)
    
    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_booking_history(self, obj) -> list:
        """Get booking history for this guest"""
        from booking.models import Booking
        from booking.serializers import BookingSerializer
        bookings = Booking.objects.filter(guest_email=obj['email']).order_by('-check_in_date')
        serializer = BookingSerializer(bookings, many=True)
        return serializer.data
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import User, Guest
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, GuestSerializer, GuestDetailedSerializer


def get_tokens_for_user(user):
    """Generate JWT tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@extend_schema(
    summary="Register a new user",
    description="Create a new user account with username and password. Returns JWT tokens upon successful registration.",
    request=UserRegisterSerializer,
    responses={201: UserSerializer, 400: {'error': 'Validation error'}},
    tags=['Authentication'],
)
@permission_classes([AllowAny])
@api_view(['POST'])
def register(request):
    """Register a new user"""
    if request.method == 'POST':
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            response_data = {
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Login user",
    description="Authenticate user with email and password. Returns JWT tokens on successful login.",
    request=UserLoginSerializer,
    responses={200: UserSerializer, 401: {'error': 'Invalid credentials'}, 400: {'error': 'Validation error'}},
    tags=['Authentication'],
)
@permission_classes([AllowAny])
@api_view(['POST'])
def login(request):
    """Login user and return JWT tokens"""
    if request.method == 'POST':
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if user.check_password(password):
                tokens = get_tokens_for_user(user)
                response_data = {
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get user profile",
    description="Retrieve the profile data of the authenticated user. Requires valid JWT token in Authorization header.",
    responses={200: UserSerializer, 401: {'error': 'Unauthorized'}, 403: {'error': 'Invalid or expired token'}},
    tags=['User'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def profile(request):
    """Return user profile data"""
    if request.method == 'GET':
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@extend_schema(
    summary="Register a new guest",
    description="Register a new guest with personal and ID proof information. Requires valid JWT token.",
    request=GuestSerializer,
    responses={201: GuestSerializer, 401: {'error': 'Unauthorized'}, 400: {'error': 'Validation error'}},
    tags=['Guest'],
)
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def guest_register(request):
    """Register a new guest"""
    # Explicit authentication check
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if request.method == 'POST':
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            guest = serializer.save()
            return Response({
                'message': 'Guest registered successfully',
                'guest': GuestSerializer(guest).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="List all guests",
    description="Retrieve a list of all registered guests. Requires valid JWT token.",
    responses={200: GuestSerializer(many=True), 401: {'error': 'Unauthorized'}},
    tags=['Guest'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def guest_list(request):
    """Return all guests"""
    # Explicit authentication check
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if request.method == 'GET':
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response({
            'message': 'Guests retrieved successfully',
            'count': guests.count(),
            'guests': serializer.data
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get guest details",
    description="Retrieve details of a specific guest by ID. Requires valid JWT token.",
    responses={200: GuestSerializer, 404: {'error': 'Guest not found'}, 401: {'error': 'Unauthorized'}},
    tags=['Guest'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def guest_retrieve(request, guest_id):
    """Return guest details"""
    # Explicit authentication check
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        try:
            guest = Guest.objects.get(id=guest_id)
        except Guest.DoesNotExist:
            return Response(
                {'error': 'Guest not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = GuestSerializer(guest)
        return Response({
            'message': 'Guest retrieved successfully',
            'guest': serializer.data
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get guest details with booking history and statistics",
    description="Retrieve detailed information about a specific guest (extracted from bookings) including booking history, total revenue, nights stayed, etc. Requires valid JWT token.",
    responses={200: GuestDetailedSerializer, 404: {'error': 'Guest not found'}, 401: {'error': 'Unauthorized'}},
    tags=['Guest'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def guest_detail_with_bookings(request, guest_email):
    """Return guest details with booking history and statistics from bookings"""
    from booking.models import Booking
    
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get the first booking for this email to extract guest details
    booking = Booking.objects.filter(guest_email=guest_email).first()
    
    if not booking:
        return Response(
            {'error': 'Guest not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get unique booking platforms for this guest
    bookings_for_guest = Booking.objects.filter(guest_email=guest_email)
    platforms = list(set([b.booking_platform for b in bookings_for_guest if b.booking_platform]))
    platforms = sorted(platforms)
    
    # Extract guest details from booking
    guest_data = {
        'name': booking.guest_name,
        'phone_number': booking.guest_phone_number,
        'email': booking.guest_email,
        'address': booking.guest_address,
        'id_proof_type': booking.guest_id_proof_type,
        'id_proof_number': booking.guest_id_proof_number,
        'last_booking_date': booking.check_in_date.strftime('%Y-%m-%d'),
        'booking_platforms': platforms,
    }
    
    serializer = GuestDetailedSerializer(guest_data)
    return Response({
        'message': 'Guest details retrieved successfully',
        'guest': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="List all guests with statistics",
    description="Retrieve a list of all unique guests (extracted from bookings) with their booking statistics including total bookings, revenue, and nights stayed. Supports pagination with page and page_size query parameters. Requires valid JWT token.",
    parameters=[
        OpenApiParameter(
            name='page',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Page number (default: 1)',
            required=False,
        ),
        OpenApiParameter(
            name='page_size',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of items per page (default: 10)',
            required=False,
        ),
    ],
    responses={200: GuestDetailedSerializer(many=True), 401: {'error': 'Unauthorized'}},
    tags=['Guest'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def guest_list_with_stats(request):
    """List all unique guests from bookings with statistics - with pagination"""
    from booking.models import Booking
    
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get pagination parameters
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 10)
    
    try:
        page = int(page)
        page_size = int(page_size)
        if page < 1 or page_size < 1:
            return Response({'error': 'page and page_size must be positive integers'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'page and page_size must be valid integers'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get unique guest emails and their information from bookings
    bookings = Booking.objects.all().order_by('-check_in_date')
    unique_guests = {}
    
    for booking in bookings:
        if booking.guest_email not in unique_guests:
            # Get unique platforms for this guest
            guest_bookings = Booking.objects.filter(guest_email=booking.guest_email)
            platforms = list(set([b.booking_platform for b in guest_bookings if b.booking_platform]))
            platforms = sorted(platforms)
            
            unique_guests[booking.guest_email] = {
                'name': booking.guest_name,
                'phone_number': booking.guest_phone_number,
                'email': booking.guest_email,
                'address': booking.guest_address,
                'id_proof_type': booking.guest_id_proof_type,
                'id_proof_number': booking.guest_id_proof_number,
                'last_booking_date': booking.check_in_date.strftime('%Y-%m-%d'),
                'booking_platforms': platforms,
            }
    
    # Convert to list
    guests_list = list(unique_guests.values())
    
    # Sort by email
    guests_list.sort(key=lambda x: x['email'])
    
    # Calculate pagination
    total_guests = len(guests_list)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_guests = guests_list[start_idx:end_idx]
    
    # Calculate total pages
    total_pages = (total_guests + page_size - 1) // page_size
    
    # Check if page is out of range
    if page > total_pages and total_guests > 0:
        return Response({'error': f'Page {page} not found. Total pages: {total_pages}'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = GuestDetailedSerializer(paginated_guests, many=True)
    
    return Response({
        'message': 'Guest list retrieved successfully',
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_guests': total_guests,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        },
        'guests': serializer.data
    }, status=status.HTTP_200_OK)
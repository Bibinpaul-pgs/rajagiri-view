from copy import deepcopy

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict
from .models import Booking
from .serializers import BookingSerializer


@extend_schema(
    summary="List all bookings",
    description="Retrieve a list of all bookings with pagination. Requires valid JWT token.",
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
    responses={200: BookingSerializer(many=True), 401: {'error': 'Authentication credentials were not provided'}},
    tags=['Booking'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_list(request):
    """List all bookings with pagination"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
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
    
    # Get all bookings
    all_bookings = Booking.objects.all().order_by('-created_at')
    
    # Calculate pagination
    total_bookings = all_bookings.count()
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    bookings = all_bookings[start_idx:end_idx]
    
    # Calculate total pages
    total_pages = (total_bookings + page_size - 1) // page_size
    
    # Check if page is out of range
    if page > total_pages and total_bookings > 0:
        return Response({'error': f'Page {page} not found. Total pages: {total_pages}'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookingSerializer(bookings, many=True)
    
    return Response({
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_bookings': total_bookings,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        },
        'bookings': serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Retrieve a specific booking",
    description="Get a booking by ID. Requires valid JWT token.",
    responses={200: BookingSerializer, 401: {'error': 'Authentication credentials were not provided'}, 404: {'error': 'Booking not found'}},
    tags=['Booking'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_retrieve(request, booking_id):
    """Retrieve a specific booking by ID"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Create a new booking",
    description="Create a new booking with guest details, room, and booking information. Guest details are stored directly with the booking. Requires valid JWT token.",
    request=BookingSerializer,
    responses={201: BookingSerializer, 400: {'error': 'Bad request'}, 401: {'error': 'Authentication credentials were not provided'}},
    tags=['Booking'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def booking_create(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Update an existing booking",
    description="Update an existing booking by ID. Requires valid JWT token.",
    request=BookingSerializer,
    responses={200: BookingSerializer, 400: {'error': 'Bad request'}, 401: {'error': 'Authentication credentials were not provided'}, 404: {'error': 'Booking not found'}},
    tags=['Booking'],
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def booking_update(request, booking_id):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookingSerializer(booking, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Delete a booking",
    description="Delete a booking by ID. Requires valid JWT token.",
    responses={204: {'description': 'Booking deleted successfully'}, 401: {'error': 'Authentication credentials were not provided'}, 404: {'error': 'Booking not found'}},
    tags=['Booking'],
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def booking_delete(request, booking_id):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    booking.delete()
    return Response({'message': 'Booking deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    summary="Get booking details grouped by check-in date",
    description="Retrieve bookings grouped by their check-in date. Supports pagination with 'page' and 'page_size' query parameters. Optionally filter by date range using 'start_date' and 'end_date' query parameters (YYYY-MM-DD format). Requires valid JWT token.",
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
            description='Number of dates per page (default: 10)',
            required=False,
        ),
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter from date (YYYY-MM-DD format)',
            required=False,
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter to date (YYYY-MM-DD format)',
            required=False,
        ),
    ],
    responses={200: {'description': 'Bookings grouped by date with pagination'}, 401: {'error': 'Authentication credentials were not provided'}},
    tags=['Booking'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_grouped_by_date(request):
    """Get bookings grouped by check-in date with pagination"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
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
    
    # Get date range from query parameters
    start_date_str = request.query_params.get('start_date', None)
    end_date_str = request.query_params.get('end_date', None)
    
    # Build query
    bookings_query = Booking.objects.all()
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            bookings_query = bookings_query.filter(check_in_date__gte=start_date)
        except ValueError:
            return Response({'error': 'Invalid start_date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            bookings_query = bookings_query.filter(check_in_date__lte=end_date)
        except ValueError:
            return Response({'error': 'Invalid end_date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all bookings and group by date
    bookings = bookings_query.order_by('check_in_date')

    # Group bookings by each date (from check_in to check_out)
    grouped_data = {}
    for booking in bookings:
        start_date = booking.check_in_date
        end_date = booking.check_out_date

        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')

            if date_key not in grouped_data:
                grouped_data[date_key] = {
                    'date': date_key,

                    'bookings': []
                }

            serializer = BookingSerializer(booking)
            serialized_data = serializer.data

            if serialized_data not in grouped_data[date_key]['bookings']:
                grouped_data[date_key]['bookings'].append(serialized_data)

            current_date += timedelta(days=1)

    result = sorted(grouped_data.values(), key=lambda x: x['date'])

    grouped = OrderedDict()

    for item in result:
        date = item.get("date")
        bookings = item.get("bookings", [])

        if date not in grouped:
            grouped[date] = []

        grouped[date].extend(bookings)  # append bookings if same date appears again

    result = [{'date': date, 'bookings': bookings} for date, bookings in grouped.items()]

    # Calculate pagination
    total_dates = len(result)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_result = result[start_idx:end_idx]
    
    # Calculate total pages
    total_pages = (total_dates + page_size - 1) // page_size
    
    # Check if page is out of range
    if page > total_pages and total_dates > 0:
        return Response({'error': f'Page {page} not found. Total pages: {total_pages}'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_dates': total_dates,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1
        },
        'grouped_bookings': paginated_result
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get booking analytics and statistics",
    description="Retrieve comprehensive booking analytics including total revenue, total bookings, monthly revenue breakdown, and occupancy rate. Requires valid JWT token.",
    responses={200: {'type': 'object'}, 401: {'error': 'Authentication credentials were not provided'}},
    tags=['Booking'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def booking_analytics(request):
    """Get booking analytics including total revenue, bookings, monthly revenue, and occupancy rate"""
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header:
        return Response({'error': 'Authentication credentials were not provided'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
    # Default date range (last 1 year)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    if start_date > end_date:
        return Response({'error': 'start_date cannot be after end_date'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get bookings in date range (bookings that overlap with the date range)
    bookings = Booking.objects.filter()
    
    # 1. Total Revenue
    total_revenue = float(bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
    
    # 2. Total Bookings
    total_bookings = bookings.count()
    
    # 3. Monthly Revenue Breakdown - Current Month Only
    current_month = datetime.now().date().replace(day=1)
    next_month = (current_month + timedelta(days=32)).replace(day=1)
    
    current_month_bookings = Booking.objects.filter(
        check_in_date__gte=current_month,
        check_in_date__lt=next_month
    )
    
    current_month_revenue = float(current_month_bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
    
    
    # 4. Occupancy Rate Calculation
    # Occupancy rate = Total nights booked / Total available room nights
    from room.models import Room
    
    # Get all bookings for occupancy calculation (regardless of date range)
    all_bookings = Booking.objects.all()
    total_rooms = Room.objects.count()
    
    if total_rooms == 0 or all_bookings.count() == 0:
        occupancy_rate = 0
    else:
        # Calculate total booked nights from all bookings
        total_booked_nights = 0
        earliest_date = None
        latest_date = None
        
        for booking in all_bookings:
            nights = (booking.check_out_date - booking.check_in_date).days
            total_booked_nights += nights
            
            if earliest_date is None or booking.check_in_date < earliest_date:
                earliest_date = booking.check_in_date
            if latest_date is None or booking.check_out_date > latest_date:
                latest_date = booking.check_out_date
        
        # Calculate total available nights based on actual booking period
        if earliest_date and latest_date:
            days_in_range = (latest_date - earliest_date).days
            total_available_nights = total_rooms * days_in_range
            
            # Calculate occupancy rate as percentage
            occupancy_rate = (total_booked_nights / total_available_nights * 100) if total_available_nights > 0 else 0
            occupancy_rate = round(occupancy_rate, 2)
        else:
            occupancy_rate = 0
    
    return Response({
        'message': 'Analytics retrieved successfully',
        'summary': {
            'total_revenue': round(total_revenue, 2),
            'total_bookings': total_bookings,
            'occupancy_rate_percentage': occupancy_rate,
            'total_rooms': total_rooms,
            'monthly_revenue': current_month_revenue,

        }
    }, status=status.HTTP_200_OK)
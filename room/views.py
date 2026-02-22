from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiRequest, OpenApiTypes
from drf_spectacular.types import OpenApiTypes
from .models import Room
from .serializers import RoomSerializer


@extend_schema(
    summary="List all rooms",
    description="Retrieve a list of all available rooms with search and filter options with pagination. Requires valid JWT token in Authorization header.",
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search rooms by name (case-insensitive)',
            required=False,
        ),
        OpenApiParameter(
            name='type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter by room type: room, house, apartment, pg',
            required=False,
            enum=['room', 'house', 'apartment', 'pg'],
        ),
        OpenApiParameter(
            name='available',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description='Filter by availability: true or false',
            required=False,
        ),
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
    responses={200: {'type': 'object'}, 401: {'error': 'Authentication credentials were not provided'}, 403: {'error': 'Invalid or expired token'}},
    tags=['Room'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def room_list(request):
    """Return all rooms with search, filter, and pagination"""
    # Check if Authorization header is present
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Explicit token validation
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
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
        
        # Start with all rooms
        rooms = Room.objects.all()
        
        # Search by name
        search = request.query_params.get('search', None)
        if search:
            rooms = rooms.filter(name__icontains=search)
        
        # Filter by type
        room_type = request.query_params.get('type', None)
        if room_type:
            rooms = rooms.filter(type=room_type)
        
        # Filter by availability
        available = request.query_params.get('available', None)
        if available is not None:
            is_available = available.lower() in ['true', '1', 'yes']
            rooms = rooms.filter(is_available=is_available)
        
        # Calculate pagination
        total_rooms = rooms.count()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_rooms = rooms[start_idx:end_idx]
        
        # Calculate total pages
        total_pages = (total_rooms + page_size - 1) // page_size
        
        # Check if page is out of range
        if page > total_pages and total_rooms > 0:
            return Response({'error': f'Page {page} not found. Total pages: {total_pages}'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RoomSerializer(paginated_rooms, many=True)
        return Response({
            'message': 'Rooms retrieved successfully',
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_rooms': total_rooms,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'rooms': serializer.data
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get room details",
    description="Retrieve details of a specific room by ID. Requires valid JWT token in Authorization header.",
    responses={200: RoomSerializer, 404: {'error': 'Room not found'}, 401: {'error': 'Authentication credentials were not provided'}, 403: {'error': 'Invalid or expired token'}},
    tags=['Room'],
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def room_retrieve(request, room_id):
    """Return room details"""
    # Check if Authorization header is present
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Explicit token validation
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'GET':
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response(
                {'error': 'Room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RoomSerializer(room)
        return Response({
            'message': 'Room retrieved successfully',
            'room': serializer.data
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Create a new room",
    description="Create a new room with optional image upload. Requires valid JWT token in Authorization header. Use multipart/form-data for image upload.",
    request=RoomSerializer,
    responses={201: RoomSerializer, 400: {'error': 'Validation error'}, 401: {'error': 'Authentication credentials were not provided'}, 403: {'error': 'Invalid or expired token'}},
    tags=['Room'],
)
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST'])
def room_create(request):
    """Create a new room"""
    # Check if Authorization header is present
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Explicit token validation
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response({
                'message': 'Room created successfully',
                'room': RoomSerializer(room).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Update a room",
    description="Update an existing room with optional image upload. Requires valid JWT token in Authorization header. Use multipart/form-data for image upload.",
    request=RoomSerializer,
    responses={200: RoomSerializer, 404: {'error': 'Room not found'}, 400: {'error': 'Validation error'}, 401: {'error': 'Authentication credentials were not provided'}, 403: {'error': 'Invalid or expired token'}},
    tags=['Room'],
)
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
@api_view(['PUT', 'PATCH'])
def room_update(request, room_id):
    """Update room details"""
    # Check if Authorization header is present
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Explicit token validation
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response(
            {'error': 'Room not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = RoomSerializer(room, data=request.data, partial=partial)
        if serializer.is_valid():
            room = serializer.save()
            return Response({
                'message': 'Room updated successfully',
                'room': RoomSerializer(room).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Delete a room",
    description="Delete an existing room. Requires valid JWT token in Authorization header.",
    responses={204: None, 404: {'error': 'Room not found'}, 401: {'error': 'Authentication credentials were not provided'}, 403: {'error': 'Invalid or expired token'}},
    tags=['Room'],
)
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def room_delete(request, room_id):
    """Delete a room"""
    # Check if Authorization header is present
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return Response(
            {'error': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Explicit token validation
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Invalid or expired token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response(
            {'error': 'Room not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'DELETE':
        room_number = room.number
        room.delete()
        return Response({
            'message': f'Room {room_number} deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)

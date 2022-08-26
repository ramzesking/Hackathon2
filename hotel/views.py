from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins, filters
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .models import Favorite, Hotel, Room, Booking, Rating, Like, Comment
from .serializers import HotelSerializer, RoomSerializer, BookingSerializer, CommentSerializer
from permissions import IsAdminOrReadOnly, IsAuthor

class HotelViewSet(ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name',]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('name', openapi.IN_QUERY, 'search hotels by name', type=openapi.TYPE_STRING)])

    @action(methods=['GET'], detail=False)
    def search(self, request):
        name = request.query_params.get('name')
        queryset = self.get_queryset()
        if name:
            queryset = queryset.filter(title__icontains=name)
        
        serializer = HotelSerializer(queryset, many=True, context={'request':request})
        return Response(serializer.data, 200)

    @action(methods=["GET"], detail=False)
    def order_by_rating(self, request):
        queryset = self.get_queryset()

        queryset = sorted(queryset, key=lambda hotel: hotel.average_rating, reverse=True)
        serializer = HotelSerializer(queryset, many=True, context={"request":request})
        return Response(serializer.data, 200)


class RoomViewSet(mixins.CreateModelMixin,
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                GenericViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price',]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]

    def check_availability(self, rdata):
        print(rdata['arrival_datetime'])
        arrival = datetime.strptime(rdata["arrival_datetime"], "%Y-%m-%d %H:%M:%S.%f")
        departure = datetime.strptime(rdata["departure_datetime"], "%Y-%m-%d %H:%M:%S.%f")
        bookings = Booking.objects.filter(room=rdata["room"])
        if bookings:
            for b in bookings:
                days1 = frozenset(range(arrival.day, departure.day + 1))
                days2 = frozenset(range(b.arrival_datetime.day, b.departure_datetime.day + 1))
                if days1.intersection(days2) and arrival.month == b.arrival_datetime.month and departure.month == b.departure_datetime.month:
                    raise Exception(f"This room is already booked for days {tuple(days1.intersection(days2))} of month {arrival.month if arrival.month == departure.month else (arrival.month, departure.month)}. Please check another dates")
        return Response("Room is available for this time")
        

    def create(self, request, *args, **kwargs):
        self.check_availability(request.data)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.check_availability(request.data)
        return super().update(request, *args, **kwargs)


class CommentViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthor, IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def toggle_like(request, r_id):
    user = request.user
    room = get_object_or_404(Room, id=r_id)

    if Like.objects.filter(user=user, room=room).exists():
        Like.objects.filter(user=user, room=room).delete()
    else:
        Like.objects.create(user=user, room=room)
    return Response("Like toggled", 200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_rating(request, h_code):
    user = request.user
    hotel = get_object_or_404(Hotel, hotel_code=h_code)
    value = request.POST.get("value")

    if not value:
        raise ValueError("Value is required")

    if Rating.objects.filter(user=user, hotel=hotel, value=value).exists():
        rating = Rating.objects.get(user=user, hotel=hotel)
        rating.value = value
        rating.save()
    else:
        Rating.objects.create(user=user, hotel=hotel, value=value)

    return Response("Rating created", 201)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def add_to_favorites(request, r_id):
    user = request.user
    room = get_object_or_404(Room, id=r_id)

    if Favorite.objects.filter(user=user, room=room).exists():
        Favorite.objects.filter(user=user, room=room).delete()
    else:
        Favorite.objects.create(user=user, room=room)
    return Response("Added to favorites", 200)

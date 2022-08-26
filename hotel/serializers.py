from rest_framework import serializers
from .models import Favorite, Hotel , Room, Booking, Comment, Like, Rating
from datetime import datetime

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context['request']
        rep = super().to_representation(instance)
        rep["rooms"] = RoomSerializer(instance.rooms.all(), many=True, context={'request': request}).data
        rep["rating"] = instance.average_rating
        rep["user_rating"] = 0
        
        if request.user.is_authenticated:
            if Rating.objects.filter(user=request.user, hotel=instance).exists():
                rating = Rating.objects.get(user=request.user, hotel=instance)
                rep["user_rating"] = rating.value

        return rep

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude =['user']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep =  super().to_representation(instance)
        rep["user"] = instance.user.email
        return rep


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["comments"] = CommentSerializer(instance.comments.all(), many=True).data
        rep["likes"] = instance.likes.all().count()
        rep["liked_by_user"] = False
        rep["favorites"] = instance.favorites.all().count()
        rep["added_to_favorites"] = False
        rep["availability"] = True

        request = self.context.get("request")

        if request.user.is_authenticated:
            rep["liked_by_user"] = Like.objects.filter(user=request.user, room=instance).exists()
            rep["added_to_favorites"] = Favorite.objects.filter(user=request.user, room=instance).exists()

        bookings = Booking.objects.filter(room=instance.id)
        if bookings:
            for b in bookings:
                days = frozenset(range(b.arrival_datetime.day, b.departure_datetime.day + 1))
                months = frozenset(range(b.arrival_datetime.month, b.departure_datetime.month + 1))
                if datetime.now().day in days and datetime.now().month in months:
                    rep["availability"] = False
                else:
                    rep["availability"] = True
        return rep


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        exclude =['user']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        return super().create(validated_data)

    def to_representation(self, instance):
        rep =  super().to_representation(instance)
        rep["user"] = instance.user.email
        return rep
    

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
    

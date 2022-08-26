from django.contrib import admin

from .models import Hotel, Room, Booking, Comment, Rating, Like

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Rating)

class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'image', 'room_type', 'status', 'max_occupancy')

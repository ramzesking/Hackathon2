from django.db import models


from account.models import User

CITY_CHOICES = [
    ("Бишкек", "Бишкек"), 
    ("Ош", "Ош"), 
    ("Чолпон-Ата", "Чолпон-Ата")]

ROOM_TYPE_CHOICES = [('1', 'type1'), ('2', 'type2'), ('3', 'type3')]

ROOM_OCCUPANCY_CHOICES = [(1, '1'), (2, '2'), (3, '3')]

    
class Hotel(models.Model):
    hotel_code = models.IntegerField(unique=True)
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='hotels', blank=True, null=True)
    address = models.CharField(max_length=200)
    postcode = models.IntegerField()
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    num_of_rooms = models.IntegerField()
    phone_number = models.CharField(max_length=13)
    star_rating = models.IntegerField()

    @property
    def average_rating(self):
        ratings = [rating.value for rating in self.ratings.all()]
        if ratings:
            return sum(ratings) / len(ratings)
        return 0

class Room(models.Model):
    room_number = models.IntegerField()
    image = models.ImageField(upload_to='rooms', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    room_type = models.CharField(max_length=100, choices=ROOM_TYPE_CHOICES)
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    max_occupancy = models.IntegerField(choices=ROOM_OCCUPANCY_CHOICES)
    
class Booking(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='bookings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='bookings', on_delete=models.CASCADE)
    booking_datetime = models.DateTimeField(auto_now_add=True)
    arrival_datetime = models.DateTimeField()
    departure_datetime = models.DateTimeField()

class Comment(models.Model):
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='comments', on_delete=models.CASCADE)

class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='likes', on_delete=models.CASCADE)

class Rating(models.Model):
    user = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, related_name='ratings', on_delete=models.CASCADE)
    value = models.IntegerField(choices=[(1,1), (2,2), (3,3), (4,4), (5,5)])

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='favorites', on_delete=models.CASCADE)


























# class Favorite(models.Model):
#     user = models.ForeignKey(User)
#     content_type = models.ForeignKey(ContentType)
#     object_id = models.PositiveIntegerField()
#     content_object = generic.GenericForeignKey('content_type', 'object_id')

#     created_on = models.DateTimeField(auto_now_add=True)
    
#     objects = FavoriteManager()

#     class Meta:
#         verbose_name = _('favorite')
#         verbose_name_plural = _('favorites')
#         unique_together = (('user', 'content_type', 'object_id'),)
    
#     def __unicode__(self):
#         return "%s likes %s" % (self.user, self.content_object)

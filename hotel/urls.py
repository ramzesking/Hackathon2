from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import HotelViewSet, RoomViewSet, CommentViewSet, BookingViewSet, add_to_favorites, toggle_like, add_rating

router = DefaultRouter()
router.register("hotel", HotelViewSet)
router.register("rooms", RoomViewSet)
router.register("comments", CommentViewSet)
router.register("booking", BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('toggle_like/<int:r_id>/', toggle_like),
    path('add_rating/<int:h_code>/', add_rating),
    path('add_to_favorites/<int:r_id>/', add_to_favorites),
]

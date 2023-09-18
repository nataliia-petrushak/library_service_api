from django.urls import path
from rest_framework import routers

from .views import BorrowingViewSet, return_borrowing

router = routers.DefaultRouter()
router.register("", BorrowingViewSet)

urlpatterns = [
    path("<int:pk>/return/", return_borrowing, name="return-borrowing")
              ] + router.urls


app_name = "borrowing"

from django.urls import path
from rest_framework import routers

from .views import PaymentViewSet, success_payment, cancel_payment

router = routers.DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("success/", success_payment, name="success-payment"),
    path("cancel/", cancel_payment, name="cancel-payment")
] + router.urls

app_name = "payment"

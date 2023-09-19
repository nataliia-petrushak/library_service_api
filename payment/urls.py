from rest_framework import routers

from .views import PaymentViewSet

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [] + router.urls

app_name = "payment"

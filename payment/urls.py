from rest_framework import routers

from .views import PaymentViewSet

router = routers.DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = router.urls

app_name = "payment"

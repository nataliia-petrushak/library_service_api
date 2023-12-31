from rest_framework import routers

from .views import BookViewSet


router = routers.DefaultRouter()
router.register("", BookViewSet)

urlpatterns = router.urls

app_name = "book"

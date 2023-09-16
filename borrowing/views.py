from rest_framework import generics, viewsets

from .permissions import IsAuthenticatedOrIsAdmin
from .serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer
)
from .models import Borrowing


class BorrowingViewSet(
    viewsets.ModelViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticatedOrIsAdmin,)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user_id=self.request.user.id)

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return BorrowingDetailSerializer
        return self.serializer_class

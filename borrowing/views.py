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

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if not self.request.user.is_staff:
            self.queryset = self.queryset.filter(user_id=self.request.user.id)

        if is_active == "True":
            self.queryset = self.queryset.filter(actual_return_date__isnull=True)

        if user_id and self.request.user.is_staff:
            user_id = self._params_to_ints(user_id)
            self.queryset = self.queryset.filter(user_id__in=user_id)

        return self.queryset

    def get_serializer_class(self):
        if self.action in ["retrieve", "update", "partial_update"]:
            return BorrowingDetailSerializer
        return self.serializer_class

from datetime import date
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
            self.queryset = self.queryset.filter(
                actual_return_date__isnull=True
            )

        if user_id and self.request.user.is_staff:
            user_id = self._params_to_ints(user_id)
            self.queryset = self.queryset.filter(user_id__in=user_id)

        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return self.serializer_class


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def return_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)

    if not borrowing.actual_return_date:
        borrowing.book.change_amount_of_inventory(increase=True)
        borrowing.actual_return_date = date.today()
        borrowing.save()
        return Response(
            {"message": "You have successfully returned this book!"},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"message": "You have already returned this book!"},
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )

from datetime import date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404

from payment.payment_session import create_payment
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsAuthenticatedOrIsAdmin
from .serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)
from .models import Borrowing


class BorrowingViewSet(
    viewsets.ModelViewSet
):
    """Users can create a book borrowing, see their borrowings only,
    and retrieve details of each one. They are forbidden to take a new book
    if there is any pending payment. Admin can update and delete borrowings"""
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
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return self.serializer_class

    @extend_schema(
        # Extra parameters added to filter
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter borrowings by actual_return_date "
                            "(if it's None - borrowing is still active)"
                            "ex. /?is_active=True",
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter borrowings by user ids. For admin only."
                            "(ex. /?user_id=1,2)",
                type={"type": "list", "items": {"type": "number"}}
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def return_borrowing(request, pk):
    """Users can return their books. If borrowing is overdue
    - there will be a new payment with the type 'FINE' created. Also,
    they can't return books twice."""
    borrowing = get_object_or_404(Borrowing, pk=pk)

    if not borrowing.actual_return_date:
        borrowing.actual_return_date = date.today()

        if borrowing.expected_return_date < borrowing.actual_return_date:
            fine = borrowing.fine
            create_payment(
                borrowing, request, payment_type="FINE", total=fine
            )

        borrowing.book.change_amount_of_inventory(increase=True)
        borrowing.save()
        serializer = BorrowingSerializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"message": "You have already returned this book!"},
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )

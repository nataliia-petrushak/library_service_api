from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import BorrowingSerializer, BorrowingDetailSerializer
from .models import Borrowing


class BorrowingReadView(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return self.serializer_class

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Payment
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    authentication_classes = (IsAuthenticated, )

    def get_object(self):
        return Payment.object.create(user_id=self.request.user.id)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(user_id=self.request.user.id)
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer


import stripe
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer
)


class PaymentViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(user_id=self.request.user.id)
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return self.serializer_class


@api_view(["GET"])
def success_payment(request):
    session_id = request.args.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment = get_object_or_404(Payment, session_id=session_id)
        payment.status = "PAID"
        payment.save()


@api_view(["GET"])
def cancel_payment(request):
    return Response({
        "message": "Payment failed. "
                   "Please proceed with the payment within 24 hours"
    })

import stripe
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer
)
from .payment_session import create_payment
from borrowing.models import Borrowing
from borrowing.notifications import send_payment_notification


class PaymentViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    viewsets.GenericViewSet
):
    """Payment sessions will be created automatically with borrowing.
    Users can see only their payment list and details of each one.
    Admin can see all the payments."""
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
    """With a successful transaction, users will get a
    notification through the Telegram bot,
    and payment changes the status to 'PAID'"""
    session_id = request.args.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment = get_object_or_404(Payment, session_id=session_id)
        payment.status = "PAID"
        payment.save()
        send_payment_notification(payment)


@api_view(["GET"])
def cancel_payment(request):
    """With canceled payment users will get a message."""
    return Response({
        "message": "Payment failed. "
                   "Please proceed with the payment within 24 hours"
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def renew_payment_session(request, pk):
    """If the payment session has expired - users can renew it
    with the creation of a new payment session."""
    old_payment = get_object_or_404(Payment, pk=pk)
    borrowing = get_object_or_404(Borrowing, pk=old_payment.borrowing_id)

    new_payment = create_payment(
        borrowing,
        request,
        payment_type=old_payment.type,
        total=old_payment.money_to_pay
    )

    serializer = PaymentSerializer(new_payment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

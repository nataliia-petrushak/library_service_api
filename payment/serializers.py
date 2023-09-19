from rest_framework import serializers

from .models import Payment
from borrowing.serializers import (
    BorrowingSerializer, BorrowingDetailSerializer
)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing_id",
            "user_id"
            "session_url",
            "session_id",
            "money_to_pay"
        )
        extra_kwargs = {"user_id": {"read_only": True}}


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing = BorrowingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "money_to_pay"
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )

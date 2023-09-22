from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Borrowing
from book.serializers import BookSerializer
from payment.payment_session import create_payment
from payment.serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer
)


class BorrowingSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        user_id = self.context["request"].user.id
        Borrowing.validate_inventory(
            attrs["book_id"],
            ValidationError
        )
        Borrowing.validate_pending_payment(user_id, ValidationError)
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "expected_return_date",
            "book_id",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        borrowing = Borrowing.objects.create(**validated_data)
        borrowing.book.change_amount_of_inventory()
        create_payment(borrowing, request)
        return borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateField(format="%Y-%m-%d")
    actual_return_date = serializers.DateField(format="%Y-%m-%d")
    expected_return_date = serializers.DateField(format="%Y-%m-%d")
    payments = PaymentListSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id",
            "payments",
        )


class BorrowingDetailSerializer(BorrowingListSerializer):
    book = BookSerializer(read_only=True)
    payments = PaymentDetailSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user_id",
            "payments",
        )

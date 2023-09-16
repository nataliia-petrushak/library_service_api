from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Borrowing
from book.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateField(format="%Y-%m-%d", read_only=True)
    actual_return_date = serializers.DateField(format="%Y-%m-%d", read_only=True)
    expected_return_date = serializers.DateField(format="%Y-%m-%d")

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_inventory(
            attrs["book_id"],
            ValidationError
        )
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "user_id"
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )

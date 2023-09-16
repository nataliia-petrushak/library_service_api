from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Borrowing
from book.models import Book
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
        extra_kwargs = {"user_id": {"read_only": True}}

    def create(self, validated_data):
        book_id = validated_data.get("book_id")
        book = get_object_or_404(Book, pk=book_id)
        book.inventory -= 1
        book.save()
        return Borrowing.objects.create(**validated_data)


class BorrowingDetailSerializer(BorrowingSerializer):
    borrow_date = serializers.DateField(format="%Y-%m-%d", required=False)
    actual_return_date = serializers.DateField(format="%Y-%m-%d", required=False)
    expected_return_date = serializers.DateField(format="%Y-%m-%d", required=False)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user_id"
        )

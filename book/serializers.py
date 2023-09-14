from rest_framework import serializers

from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee"
        )


class BookListSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "daily_fee")

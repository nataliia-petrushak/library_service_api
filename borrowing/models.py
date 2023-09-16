from django.db import models
from rest_framework.generics import get_object_or_404

from book.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book_id = models.IntegerField()
    user_id = models.IntegerField()

    @property
    def book(self) -> Book:
        return get_object_or_404(Book, pk=self.book_id)

    @property
    def user(self) -> User:
        return get_object_or_404(User, pk=self.user_id)

    @staticmethod
    def validate_inventory(book_id, error_to_raise):
        book = get_object_or_404(Book, pk=book_id)
        if book.inventory < 1:
            raise error_to_raise("There are no books in inventory to borrow")

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

    def book(self) -> Book:
        return get_object_or_404(Book, pk=self.book_id)

    def user(self) -> User:
        return get_object_or_404(User, pk=self.user_id)

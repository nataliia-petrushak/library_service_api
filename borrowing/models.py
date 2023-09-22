from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.generics import get_object_or_404

from book.models import Book
from user.models import User
from payment.models import Payment

from borrowing.management.commands.send_notification import notification


class Borrowing(models.Model):
    FINE_MULTIPLIER = 2

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

    @property
    def payments(self) -> Payment:
        return Payment.objects.filter(borrowing_id=self.pk)

    @staticmethod
    def validate_inventory(book_id, error_to_raise):
        book = get_object_or_404(Book, pk=book_id)
        if book.inventory < 1:
            raise error_to_raise("There are no books in inventory to borrow")

    @staticmethod
    def validate_pending_payment(user_id: int, error_to_raise):
        payments = Payment.objects.filter(user_id=user_id, status="PAID")

        if not payments.exists():
            raise error_to_raise("You have not finished your paying. "
                                 "Please finish it before borrowing a new book.")

    @property
    def fine(self) -> int:
        fine_per_day = 2
        days = (self.actual_return_date - self.expected_return_date).days
        fine_amount = days * fine_per_day * self.FINE_MULTIPLIER
        return fine_amount


@receiver(post_save, sender=Borrowing)
def create_borrowing_notifications(sender, instance, created, **kwargs):
    book = get_object_or_404(Book, pk=instance.book_id)
    message = f"You have borrowed a book:\n'{book.title}'." \
              f"\nExpected return date:" \
              f"\n{instance.expected_return_date}\n" \
              f"Price:\n" \
              f"{book.daily_fee} $"
    if created:
        notification(message)

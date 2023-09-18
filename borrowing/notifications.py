import requests
from django.conf import settings
from rest_framework.generics import get_object_or_404
from book.models import Book


def send_borrowing_notification(sender, instance, created, **kwargs):
    book = get_object_or_404(Book, pk=instance.book_id)
    if created:
        message = f"You have borrowed {book.title}." \
                  f"\nExpected return date:" \
                  f"\n{instance.expected_return_date}\n" \
                  f"Price:\n" \
                  f"{book.daily_fee} $"
        chat_id = settings.CHAT_ID,
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        requests.post(url, data)

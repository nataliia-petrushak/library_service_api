import datetime
import logging

from borrowing.management.commands.send_notification import notification
from django.db.models import Q

from .models import Borrowing

logger = logging.getLogger(__name__)


def overdue_borrowings():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return Borrowing.objects.filter(
        Q(expected_return_date__lte=tomorrow)
        & Q(actual_return_date__isnull=True)
    )


def send_overdue_borrowing_notification():
    borrowings = overdue_borrowings()
    if not borrowings:
        notification("There are no overdue book borrowings today")

    for borrowing in borrowings:
        logger.info(f"Creating message for book borrowing id: {borrowing.id}")
        message = f"The expiration date of your book borrowing is " \
                  f"{borrowing.expected_return_date}.\n" \
                  f"Please return the book '{borrowing.book.title}' " \
                  f"by that time."
        notification(message)
        logger.info(f"The message was successfully sent")

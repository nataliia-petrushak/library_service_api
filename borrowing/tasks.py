from celery import shared_task
from .notifications import send_overdue_borrowing_notification


@shared_task
def overdue_borrowing_notifications():
    send_overdue_borrowing_notification()

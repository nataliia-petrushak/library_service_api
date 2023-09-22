from celery import shared_task
from .check_sessions import check_expiration_sessions


@shared_task
def check_stripe_expired_sessions():
    check_expiration_sessions()

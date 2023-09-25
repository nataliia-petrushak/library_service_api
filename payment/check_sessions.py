from django.utils import timezone
import logging

from .models import StripeSession

logger = logging.getLogger(__name__)


def check_expiration_sessions():
    current_time = timezone.now()
    expired_sessions = StripeSession.objects.filter(
        expiration_time__lte=current_time, is_expired=False
    )
    if not expired_sessions:
        logger.info(f"There are no expired sessions")

    for session in expired_sessions:
        session.cancel_payment_session()
        logger.info(f"Session {session.id} and payment {session.payment_id} is expired")

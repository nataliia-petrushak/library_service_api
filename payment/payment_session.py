import os
import stripe
from django.db import transaction
from django.utils import timezone
from rest_framework.reverse import reverse

from .models import Payment, StripeSession

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_stripe_session(borrowing, request, total):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(total * 100),
                    "product_data": {
                        "name": borrowing.book.title
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(
            reverse("payment:success-payment"
                    )) + f"?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=request.build_absolute_uri(
            reverse("payment:cancel-payment")
        )
    )


def create_model_stripe_session(borrowing, session, payment):
    expiration_time = timezone.now() + timezone.timedelta(minutes=2)
    StripeSession.objects.create(
        session_id=session.id,
        payment_id=payment.pk,
        user_id=borrowing.user_id,
        expiration_time=expiration_time
    )


def create_payment(
        borrowing, request, payment_type: str = "PAYMENT", total=None
) -> Payment:

    if not total:
        total = borrowing.book.daily_fee

    with transaction.atomic():
        session = create_stripe_session(borrowing, request, total)

        payment = Payment.objects.create(
            status="PENDING",
            type=payment_type,
            borrowing_id=borrowing.id,
            user_id=borrowing.user_id,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=total
        )
        create_model_stripe_session(borrowing, session, payment)

        return payment

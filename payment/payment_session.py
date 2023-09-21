import os
import stripe
from rest_framework.reverse import reverse

from .models import Payment

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_payment_session(borrowing, request, payment):

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(payment * 100),
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
    return session


def create_payment(
        borrowing,
        request,
        payment_type: str = "PAYMENT",
        payment=None
):

    if not payment:
        payment = borrowing.book.daily_fee

    session = create_payment_session(borrowing, request, payment)
    Payment.objects.create(
        status="PENDING",
        type=payment_type,
        borrowing_id=borrowing.id,
        user_id=borrowing.user_id,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=payment
    )

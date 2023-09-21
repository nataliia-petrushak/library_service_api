import os
import stripe
from rest_framework.reverse import reverse

from .models import Payment

stripe.api_key = os.getenv("STRIPE_API_KEY")


def create_payment_session(borrowing, request):
    total_price = int(borrowing.book.daily_fee * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": total_price,
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


def create_payment(borrowing, request):
    session = create_payment_session(borrowing, request)
    Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowing_id=borrowing.id,
        user_id=borrowing.user_id,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=borrowing.book.daily_fee
    )

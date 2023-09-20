import os
import stripe

from .models import Payment

stripe.api_key = os.getenv("API_KEY")


def create_payment_session(borrowing):
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
        success_url="http://localhost:8000/api/payments/",
        cancel_url="http://localhost:8000/api/payments/"
    )
    return session


def create_payment(borrowing):
    session = create_payment_session(borrowing)
    Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowing_id=borrowing.id,
        user_id=borrowing.user_id,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=borrowing.book.daily_fee
    )

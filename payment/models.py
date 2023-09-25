import stripe
from django.db import models
from rest_framework.generics import get_object_or_404


class Payment(models.Model):
    STATUS_CHOICE = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("EXPIRED", "Expired")
    ]
    TYPE_CHOICE = [("PAYMENT", "Payment"), ("FINE", "Fine")]

    status = models.CharField(max_length=7, choices=STATUS_CHOICE)
    type = models.CharField(max_length=7, choices=TYPE_CHOICE)
    borrowing_id = models.IntegerField()
    user_id = models.IntegerField()
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)


class StripeSession(models.Model):
    session_id = models.CharField(max_length=255)
    payment_id = models.IntegerField()
    user_id = models.IntegerField()
    expiration_time = models.DateTimeField()
    is_expired = models.BooleanField(default=False)

    @property
    def payment(self) -> Payment:
        return get_object_or_404(Payment, pk=self.payment_id)

    def cancel_payment_session(self):
        stripe.checkout.Session.expire(self.session_id)
        payment = self.payment

        self.is_expired = True
        self.save()

        payment.status = "EXPIRED"
        payment.save()

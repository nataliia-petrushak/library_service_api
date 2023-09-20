from django.db import models

from rest_framework.generics import get_object_or_404


class Payment(models.Model):
    STATUS_CHOICE = [("PENDING", "Pending"), ("PAID", "Paid")]
    TYPE_CHOICE = [("PAYMENT", "Payment"), ("FINE", "Fine")]

    status = models.CharField(max_length=7, choices=STATUS_CHOICE)
    type = models.CharField(max_length=7, choices=TYPE_CHOICE)
    borrowing_id = models.IntegerField()
    user_id = models.IntegerField()
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)

from django.db import models

from borrowing.models import Borrowing
from rest_framework.generics import get_object_or_404


class Payment(models.Model):
    STATUS_CHOICE = [("PN", "PENDING"), ("PD", "PAID")]
    TYPE_CHOICE = [("P", "PAYMENT"), ("F", "FINE")]

    status = models.CharField(max_length=2, choices=STATUS_CHOICE)
    type = models.CharField(max_length=1, choices=TYPE_CHOICE)
    borrowing_id = models.IntegerField()
    user_id = models.IntegerField()
    session_url = models.URLField()
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)

    def borrowing(self) -> Borrowing:
        return get_object_or_404(Borrowing, pk=self.borrowing_id)

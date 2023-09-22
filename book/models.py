from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.generics import get_object_or_404


class Book(models.Model):
    COVER_CHOICES = [("H", "HARD"), ("S", "SOFT")]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=1, choices=COVER_CHOICES)
    inventory = models.IntegerField(
        validators=[MinValueValidator(limit_value=0)]
    )
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def change_amount_of_inventory(self, increase=False):
        if increase:
            self.inventory += 1
        else:
            self.inventory -= 1
        self.save()

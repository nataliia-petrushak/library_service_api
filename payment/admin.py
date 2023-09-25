from django.contrib import admin

from .models import Payment, StripeSession


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "status", "type", "borrowing_id", "user_id", "money_to_pay"
    )
    list_filter = ("status", "type")
    search_fields = ("borrowing_id", "user_id")


@admin.register(StripeSession)
class StripeSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "session_id", "user_id", "expiration_time", "is_expired"
    )
    list_filter = ("is_expired", )
    search_fields = ("expiration_time",)

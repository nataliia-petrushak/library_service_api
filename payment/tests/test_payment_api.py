import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment, StripeSession
from payment.serializers import PaymentListSerializer, PaymentDetailSerializer

PAYMENT_URL = reverse("payment:payment-list")


def sample_book(**params):
    defaults = {
        "title": "Sample book",
        "author": "Test Author",
        "cover": "S",
        "inventory": 5,
        "daily_fee": 10.0,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def sample_borrowing(**params):
    book = sample_book()
    defaults = {
        "expected_return_date": datetime.date(2023, 9, 29),
        "book_id": book.id,
        "user_id": 1
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


def sample_payment(**params):
    borrowing = sample_borrowing()

    defaults = {
        "status": "PENDING",
        "type": "PAYMENT",
        "borrowing_id": borrowing.id,
        "user_id": borrowing.user_id,
        "session_url": "http:/example.com",
        "session_id": "fjnvdkjfnvkjd",
        "money_to_pay": borrowing.book.daily_fee
    }
    defaults.update(params)
    return Payment.objects.create(**defaults)


def sample_stripe_session(**params):
    payment = sample_payment()

    defaults = {
        "session_id": payment.session_id,
        "payment_id": payment.pk,
        "user_id": payment.user_id,
        "expiration_time": datetime.date.today() + datetime.timedelta(days=1)
    }
    defaults.update(params)
    return StripeSession.objects.create(**defaults)


def detail_url(payment_id):
    return reverse("payment:payment-detail", args=[payment_id])


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_user_can_see_only_his_own_payments(self):
        user_2 = get_user_model().objects.create_user(
            "user2@user.com",
            "user2pass"
        )
        payment_1 = sample_payment()
        payment_2 = sample_payment(user_id=user_2.id)
        payment_3 = sample_payment()

        res = self.client.get(PAYMENT_URL)

        serializer_1 = PaymentListSerializer(payment_1)
        serializer_2 = PaymentListSerializer(payment_2)
        serializer_3 = PaymentListSerializer(payment_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)
        self.assertIn(serializer_3.data, res.data)

    def test_detail_payment(self):

        payment = sample_payment()

        url = detail_url(payment.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(payment.user_id, self.user.id)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_admin_can_see_all_payments(self):
        user_1 = get_user_model().objects.create_user(
            "user1@user.com",
            "user1pass"
        )
        user_2 = get_user_model().objects.create_user(
            "user2@user.com",
            "user2pass"
        )
        user_3 = get_user_model().objects.create_user(
            "user3@user.com",
            "user3pass"
        )

        payment_1 = sample_payment(user_id=user_1.id)
        payment_2 = sample_payment(user_id=user_2.id)
        payment_3 = sample_payment(user_id=user_3.id)

        res = self.client.get(PAYMENT_URL)

        serializer_1 = PaymentListSerializer(payment_1)
        serializer_2 = PaymentListSerializer(payment_2)
        serializer_3 = PaymentListSerializer(payment_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data)
        self.assertIn(serializer_2.data, res.data)
        self.assertIn(serializer_3.data, res.data)

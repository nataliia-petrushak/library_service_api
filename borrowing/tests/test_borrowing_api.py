import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from payment.models import Payment
from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer
)

BORROWING_URL = reverse("borrowing:borrowing-list")


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


def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id):
    return reverse("borrowing:return-borrowing", args=[borrowing_id])


class UnauthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing()
        sample_borrowing()

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_is_active(self):

        borrowing1 = sample_borrowing(
            actual_return_date=datetime.date.today(),
        )
        borrowing2 = sample_borrowing()

        res = self.client.get(
            BORROWING_URL, {"is_active": "True"}
        )

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)

        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)

    def test_users_can_see_only_their_borrowings(self):
        user2 = get_user_model().objects.create_user(
            "user1@user.com",
            "user1pass"
        )

        borrowing1 = sample_borrowing()
        borrowing2 = sample_borrowing(user_id=user2.id)
        borrowing3 = sample_borrowing()

        res = self.client.get(BORROWING_URL)

        serializer1 = BorrowingListSerializer(borrowing1)
        serializer2 = BorrowingListSerializer(borrowing2)
        serializer3 = BorrowingListSerializer(borrowing3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer3.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_create_borrowings_with_payment(self):

        book = sample_book()
        payload = {
            "expected_return_date": datetime.date(2023, 9, 29),
            "book_id": book.id,
        }

        res = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(borrowing.payments.exists())
        self.assertEqual(borrowing.user, self.user)

    def test_create_borrowing_forbidden_if_book_inventory_0(self):
        book = sample_book(inventory=0)

        payload = {
            "expected_return_date": datetime.date(2025, 3, 24),
            "book_id": book.id
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("There are no books in inventory to borrow", str(res.data))

    def test_return_borrowing(self):
        borrowing = sample_borrowing()
        today = datetime.date.today()

        url = return_url(borrowing.id)
        res = self.client.post(url)

        new_borrowing = Borrowing.objects.get(id=borrowing.id)
        serializer = BorrowingSerializer(new_borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(new_borrowing.actual_return_date, today)
        self.assertEqual(serializer.data, res.data)

    def test_return_borrowing_twice_forbidden(self):

        borrowing = sample_borrowing(
            user_id=self.user.id,
            actual_return_date=datetime.date.today()
        )

        url = return_url(borrowing.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

#
    def test_return_overdue_borrowings_with_fine_payment(self):
        borrowing = sample_borrowing(
            expected_return_date=(datetime.date.today()
                                  - datetime.timedelta(days=1))
        )

        url = return_url(borrowing.id)
        res = self.client.post(url)

        new_borrowing = Borrowing.objects.get(id=borrowing.id)

        is_fine_type = new_borrowing.payments.filter(type="FINE")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(is_fine_type.exists())

#
    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_put_borrowing_forbidden(self):
        borrowing = sample_borrowing()
        book = sample_book()

        payload = {
            "expected_return_date": datetime.date.today(),
            "book_id": book.id
        }

        url = detail_url(borrowing.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_borrowing_forbidden(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrowing_forbidden_with_pending_payments(self):
        borrowing = sample_borrowing()
        Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing_id=borrowing.id,
            user_id=borrowing.user_id,
            session_url="http://example.com",
            session_id="dcnskdjvndil",
            money_to_pay=borrowing.book.daily_fee
        )
        book = sample_book()

        payload = {
            "expected_return_date": datetime.date.today(),
            "book_id": book.id
        }

        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have not finished your paying. "
                      "Please finish it before borrowing a new book.", str(res.data))


class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_filter_borrowings_by_user_ids(self):
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

        borrowing_1 = sample_borrowing(user_id=user_1.id)
        borrowing_2 = sample_borrowing(user_id=user_2.id)
        borrowing_3 = sample_borrowing(user_id=user_3.id)

        res = self.client.get(BORROWING_URL, {"user_id": f"{user_1.id}, {user_2.id}"})

        serializer1 = BorrowingListSerializer(borrowing_1)
        serializer2 = BorrowingListSerializer(borrowing_2)
        serializer3 = BorrowingListSerializer(borrowing_3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

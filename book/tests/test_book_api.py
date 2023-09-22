from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from book.models import Book
from book.serializers import BookListSerializer

BOOK_URL = reverse("book:book-list")


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


def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


class UsersLibraryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def authorise(self):
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_auth_not_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_movies(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookListSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_unauthorised_users_forbidden(self):
        payload = {
            "title": "Test",
            "author": "Test Author",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 10.0,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authorised_users_forbidden(self):
        self.authorise()

        payload = {
            "title": "Test",
            "author": "Test Author",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 10.0,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_authorised_users_not_allowed(self):
        self.authorise()

        payload = {
            "title": "Test",
            "author": "Test Author",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 10.0,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_unauthorised_users_not_allowed(self):

        payload = {
            "title": "Test",
            "author": "Test Author",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 10.0,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_authorised_users_not_allowed(self):
        self.authorise()

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_unauthorised_users_not_allowed(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Test",
            "author": "Test Author",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 10.0,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        movie = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(movie, key))

    def test_put_book(self):

        payload = {
            "title": "Test",
            "author": "Test Author",
            "cover": "S",
            "inventory": 5,
            "daily_fee": 10.0,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_book(self):

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

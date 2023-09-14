from rest_framework import viewsets

from .permissions import IsAdminOrReadOnly
from .models import Book
from .serializers import BookSerializer, BookListSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return self.serializer_class

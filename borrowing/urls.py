from django.urls import path

from .views import BorrowingReadView

borrowing_list = BorrowingReadView.as_view(actions={"get": "list"})
borrowing_detail = BorrowingReadView.as_view(actions={"get": "retrieve"})

urlpatterns = [
    path("", borrowing_list, name="borrowing-list"),
    path("<int:pk>/", borrowing_detail, name="borrowing-detail")
]


app_name = "borrowing"

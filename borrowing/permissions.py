from rest_framework.permissions import BasePermission


class IsAuthenticatedOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in ["POST", "GET"]
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff
                )
        )

from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and is a staff member or superuser
        return request.user and request.user.is_authenticated and request.user.is_admin

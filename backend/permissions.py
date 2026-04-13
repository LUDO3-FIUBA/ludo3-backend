from rest_framework import permissions


class IsStudent(permissions.BasePermission):# TODO: check status
    """
    Custom permission to only allow students
    """

    def has_permission(self, request, view):
        return request.user.is_student


class IsTeacher(permissions.BasePermission):
    """
    Custom permission to only allow students
    """

    def has_permission(self, request, view):
        return request.user.is_teacher


class IsAdmin(permissions.BasePermission):
    """Custom permission to only allow staff/admin users"""

    def has_permission(self, request, view):
        return request.user.is_staff

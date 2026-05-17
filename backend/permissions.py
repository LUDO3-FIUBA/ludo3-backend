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


class IsTeacherOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_teacher or request.user.is_staff


class IsSuperAdmin(permissions.BasePermission):
    """Permission that only allows full super-admin users (is_superuser=True)."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsBedelia(permissions.BasePermission):
    """Permission that only allows bedelía staff users."""

    def has_permission(self, request, view):
        return is_bedelia(request.user)


def get_admin_department_id(user):
    """Returns the department id this admin is scoped to, or None for super admins / non-admins."""
    if not user.is_authenticated or not user.is_staff:
        return None
    if user.is_superuser:
        return None
    staff = getattr(user, 'staff', None)
    if staff is None:
        return None
    return staff.department_id


def is_bedelia(user):
    """True for staff users marked as bedelía (not super admin, not a department admin)."""
    if not user.is_authenticated or not user.is_staff or user.is_superuser:
        return False
    staff = getattr(user, 'staff', None)
    return bool(staff and staff.is_bedelia)

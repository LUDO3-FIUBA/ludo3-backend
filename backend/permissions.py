from rest_framework import permissions


def get_user_ownership_memberships(user):
    """
    Returns a QuerySet of FormOwnershipMember rows for the entity (department or
    secretary) that this admin user is linked to via their Staff record.

    Returns an empty QuerySet if the user has no Staff, is a super admin, or is
    not a staff user at all — callers must gate super-admin behaviour separately.
    """
    from backend.models.form_ownership import FormOwnershipMember

    if not user.is_authenticated or not user.is_staff:
        return FormOwnershipMember.objects.none()
    if user.is_superuser:
        return FormOwnershipMember.objects.none()

    staff = getattr(user, 'staff', None)
    if staff is None:
        return FormOwnershipMember.objects.none()

    if staff.department_id is not None:
        return FormOwnershipMember.objects.filter(
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=staff.department_id,
        )
    if staff.secretary_id is not None:
        return FormOwnershipMember.objects.filter(
            entity_type=FormOwnershipMember.SECRETARY,
            entity_id=staff.secretary_id,
        )
    return FormOwnershipMember.objects.none()


class IsFormOwnershipMember(permissions.BasePermission):
    """
    Object-level read permission: the requesting admin's entity must be a member
    of the form's ownership group.  Super admins always pass.

    Intended for use on FormViewSet actions that read a specific form.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # obj is a Form instance; check membership in its group.
        memberships = get_user_ownership_memberships(request.user)
        return memberships.filter(group=obj.ownership_group).exists()


class IsFormOwnershipEditor(permissions.BasePermission):
    """
    Object-level write permission: the requesting admin's entity must be an
    *editor* in the form's ownership group.  Super admins always pass.

    Intended for create/update/destroy on FormViewSet.
    For create the group is in the payload, not on an existing object, so
    callers should also use the helper directly when no object is available yet.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        memberships = get_user_ownership_memberships(request.user)
        return memberships.filter(group=obj.ownership_group, is_editor=True).exists()


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

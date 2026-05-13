import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.department import Department
from .models.staff import Staff
from .models.user import User

logger = logging.getLogger(__name__)

DEFAULT_DEPT_ADMIN_PASSWORD = 'test123'


def _next_dept_admin_dni():
    """Returns the next sequential 8-digit DNI for a new dept admin."""
    existing = (
        Staff.objects
        .filter(department__isnull=False, user__dni__regex=r'^\d{8}$')
        .values_list('user__dni', flat=True)
    )
    max_n = 0
    for dni in existing:
        try:
            max_n = max(max_n, int(dni))
        except (TypeError, ValueError):
            continue
    return f"{max_n + 1:08d}"


@receiver(post_save, sender=Department)
def create_admin_for_new_department(sender, instance, created, **kwargs):
    if not created:
        return
    if Staff.objects.filter(department=instance).exists():
        return

    dni = _next_dept_admin_dni()
    email = f"admin.dept{instance.id}@dept.fi.uba.ar"

    if User.objects.filter(dni=dni).exists() or User.objects.filter(email=email).exists():
        logger.warning(
            "Skipping dept admin auto-creation for department %s: dni=%s or email=%s already exists.",
            instance.id, dni, email,
        )
        return

    user = User(
        dni=dni,
        email=email,
        first_name='Admin',
        last_name=(instance.name or 'Departamento')[:50],
        is_staff=True,
        is_superuser=False,
        is_student=False,
        is_teacher=False,
    )
    user.set_password(DEFAULT_DEPT_ADMIN_PASSWORD)
    user.save()

    Staff.objects.create(user=user, department=instance, department_siu_id=0)

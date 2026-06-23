"""Demo DB cleanup — runs inside the web container against the LOCAL db.

Keeps: all is_staff users (dept admins, bedelia, superuser) + 5 named team members.
Deletes: all finals (exams) and commissions (cascades), and every other user.
Departments are kept untouched.
"""
from django.db import transaction
from backend.models.user import User
from backend.models.commission import Commission
from backend.models.final import Final
from backend.models.department import Department

# The 5 named people (by dni — stable identifier).
KEEP_DNIS = {
    "13123123",  # Pablo Cosso
    "41779246",  # Gonzalo Gordyn Biello
    "41835723",  # Joaquin Andresen
    "43459394",  # Valentina Lanzillotta
    "42150053",  # Matias Sebastian Merlo Gonzalez
}

with transaction.atomic():
    print("BEFORE:",
          "users", User.objects.count(),
          "commissions", Commission.objects.count(),
          "finals", Final.objects.count(),
          "departments", Department.objects.count())

    # 1) Exams: delete all finals (cascades final_exams).
    f_deleted = Final.objects.all().delete()
    print("finals deleted:", f_deleted)

    # 2) Commissions: delete all (cascades teacher_roles, semesters -> evals/attendance/inscriptions).
    c_deleted = Commission.objects.all().delete()
    print("commissions deleted:", c_deleted)

    # 3) Users: keep is_staff (dept admins/bedelia/superuser) + the 5 named. Delete the rest.
    to_delete = User.objects.exclude(is_staff=True).exclude(dni__in=KEEP_DNIS)
    print("users to delete:", to_delete.count())
    for u in to_delete.order_by("id"):
        print("  - deleting", u.id, u.first_name, u.last_name, u.email, u.dni)
    u_deleted = to_delete.delete()
    print("users deleted:", u_deleted)

    print("AFTER:",
          "users", User.objects.count(),
          "commissions", Commission.objects.count(),
          "finals", Final.objects.count(),
          "departments", Department.objects.count())

    # Sanity: the 5 named must survive.
    survivors = User.objects.filter(dni__in=KEEP_DNIS).count()
    assert survivors == len(KEEP_DNIS), f"expected {len(KEEP_DNIS)} named survivors, got {survivors}"
    print("named survivors OK:", survivors)

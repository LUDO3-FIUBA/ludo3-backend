from datetime import datetime
from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from backend.client.siu_client import SiuClient
from backend.models import Final
from backend.models.department import Department
from backend.models.staff import Staff
from backend.services.notification_service import NotificationService
from ..factories import (CommissionFactory, FinalFactory, TeacherFactory,
                         UserFactory)


def _make_super_admin():
    return UserFactory(is_staff=True, is_superuser=True, is_student=False, is_teacher=False)


def _make_dept_admin(department):
    user = UserFactory(is_staff=True, is_superuser=False, is_student=False, is_teacher=False)
    Staff.objects.create(user=user, department=department, department_siu_id=0)
    return user


class AdminFinalsViewsTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Computación")
        self.other_department = Department.objects.create(name="Matemática")

        self.super_admin = _make_super_admin()
        self.dept_admin = _make_dept_admin(self.department)

        self.teacher = TeacherFactory()
        self.commission_in_dept = CommissionFactory(
            chief_teacher=self.teacher,
            department=self.department,
        )
        self.commission_other_dept = CommissionFactory(
            chief_teacher=self.teacher,
            department=self.other_department,
        )

    def _final_for(self, commission, status_=Final.Status.DRAFT):
        final = FinalFactory(teacher=commission.chief_teacher, status=status_,
                             subject_siu_id=commission.subject_siu_id)
        final.commissions.add(commission)
        return final

    def test_list_requires_admin(self):
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get("/api/admin/finals/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dept_admin_only_sees_finals_of_own_department(self):
        own = self._final_for(self.commission_in_dept)
        self._final_for(self.commission_other_dept)

        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.get("/api/admin/finals/?status=DF")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([f['id'] for f in response.data], [own.id])

    def test_super_admin_sees_all_finals(self):
        a = self._final_for(self.commission_in_dept)
        b = self._final_for(self.commission_other_dept)

        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get("/api/admin/finals/?status=DF")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(f['id'] for f in response.data), sorted([a.id, b.id]))

    def test_approve_changes_status_and_calls_siu(self):
        final = self._final_for(self.commission_in_dept)
        self.client.force_authenticate(user=self.dept_admin)

        with mock.patch.object(SiuClient, "create_final", return_value={"id": 999}):
            with mock.patch.object(NotificationService, "notify_date_approved", return_value=None) as notify:
                response = self.client.post(f"/api/admin/finals/{final.id}/approve/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        final.refresh_from_db()
        self.assertEqual(final.status, Final.Status.OPEN)
        self.assertEqual(final.siu_id, 999)
        notify.assert_called_once()

    def test_approve_rejects_non_draft(self):
        final = self._final_for(self.commission_in_dept, status_=Final.Status.OPEN)
        self.client.force_authenticate(user=self.dept_admin)

        response = self.client.post(f"/api/admin/finals/{final.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dept_admin_cannot_approve_other_dept(self):
        final = self._final_for(self.commission_other_dept)
        self.client.force_authenticate(user=self.dept_admin)

        response = self.client.post(f"/api/admin/finals/{final.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reject_changes_status(self):
        final = self._final_for(self.commission_in_dept)
        self.client.force_authenticate(user=self.dept_admin)

        response = self.client.post(f"/api/admin/finals/{final.id}/reject/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        final.refresh_from_db()
        self.assertEqual(final.status, Final.Status.REJECTED)
        self.assertEqual(final.commissions.count(), 1)

    def test_finals_without_department_only_visible_to_super_admin(self):
        commission_no_dept = CommissionFactory(chief_teacher=self.teacher, department=None)
        final = self._final_for(commission_no_dept)

        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.get("/api/admin/finals/?status=DF")
        self.assertEqual([f['id'] for f in response.data], [])

        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get("/api/admin/finals/?status=DF")
        self.assertIn(final.id, [f['id'] for f in response.data])

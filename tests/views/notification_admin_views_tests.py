from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Notification, Staff
from backend.models.user import User
from ..factories import (AdminUserFactory, DepartmentFactory, DeptStaffFactory,
                         SecretaryStaffFactory, StudentFactory, TeacherFactory)

URL = "/api/admin/notifications/"


class NotificationAdminAccessTests(APITestCase):
    def setUp(self):
        self.dept = DepartmentFactory()
        self.super_admin = AdminUserFactory()
        self.dept_admin = DeptStaffFactory(department=self.dept).user
        StudentFactory()  # at least one recipient for 'students'

    def _payload(self, **overrides):
        payload = {
            'title': 'Aviso',
            'message': 'Mensaje',
            'recipient_groups': ['students'],
        }
        payload.update(overrides)
        return payload

    def test_unauthenticated_returns_401(self):
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_cannot_create(self):
        student = StudentFactory()
        self.client.force_authenticate(user=student.user)
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_create(self):
        teacher = TeacherFactory()
        self.client.force_authenticate(user=teacher.user)
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_secretary_admin_cannot_create(self):
        secretary_admin = SecretaryStaffFactory().user
        self.client.force_authenticate(user=secretary_admin)
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bedelia_cannot_create(self):
        bedelia_admin = DeptStaffFactory(department=None, secretary=None).user
        Staff.objects.filter(user=bedelia_admin).update(is_bedelia=True, department=None)
        self.client.force_authenticate(user=bedelia_admin)
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dept_admin_create_auto_assigns_department(self):
        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        notification = Notification.objects.get(id=response.data['id'])
        self.assertEqual(notification.department_id, self.dept.id)
        self.assertEqual(response.data['department']['id'], self.dept.id)
        self.assertEqual(response.data['department']['name'], self.dept.name)

    def test_dept_admin_cannot_override_department(self):
        other_dept = DepartmentFactory()
        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.post(URL, self._payload(department_id=other_dept.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notification = Notification.objects.get(id=response.data['id'])
        # ignored: still tagged with its own department
        self.assertEqual(notification.department_id, self.dept.id)

    def test_super_admin_can_create_without_department(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notification = Notification.objects.get(id=response.data['id'])
        self.assertIsNone(notification.department_id)
        self.assertIsNone(response.data['department'])

    def test_super_admin_can_create_with_department(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(URL, self._payload(department_id=self.dept.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notification = Notification.objects.get(id=response.data['id'])
        self.assertEqual(notification.department_id, self.dept.id)

    def test_super_admin_invalid_department_id_returns_400(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(URL, self._payload(department_id=99999), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dept_admin_list_scoped_to_own_department(self):
        other_dept = DepartmentFactory()
        other_admin = DeptStaffFactory(department=other_dept).user
        student = StudentFactory()

        self.client.force_authenticate(user=self.dept_admin)
        self.client.post(URL, self._payload(title='Mio'), format='json')

        self.client.force_authenticate(user=other_admin)
        self.client.post(URL, self._payload(title='Ajeno'), format='json')

        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [n['title'] for n in response.data]
        self.assertIn('Mio', titles)
        self.assertNotIn('Ajeno', titles)

    def test_super_admin_list_sees_all(self):
        other_dept = DepartmentFactory()
        other_admin = DeptStaffFactory(department=other_dept).user
        self.client.force_authenticate(user=self.dept_admin)
        self.client.post(URL, self._payload(title='Mio'), format='json')
        self.client.force_authenticate(user=other_admin)
        self.client.post(URL, self._payload(title='Ajeno'), format='json')

        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [n['title'] for n in response.data]
        self.assertIn('Mio', titles)
        self.assertIn('Ajeno', titles)

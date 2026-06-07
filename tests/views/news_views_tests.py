from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import News
from ..factories import (AdminUserFactory, DepartmentFactory, DeptStaffFactory,
                         SecretaryStaffFactory, StudentFactory, TeacherFactory)

LIST_URL = "/api/news/"


def _detail_url(pk):
    return f"/api/news/{pk}/"


class NewsViewsTests(APITestCase):
    def setUp(self):
        self.dept = DepartmentFactory(name='Computacion')
        self.other_dept = DepartmentFactory(name='Matematica')
        self.super_admin = AdminUserFactory()
        self.dept_admin = DeptStaffFactory(department=self.dept).user
        self.other_dept_admin = DeptStaffFactory(department=self.other_dept).user

    def _payload(self, **overrides):
        payload = {
            'title': 'Novedad',
            'description': 'Una novedad importante',
            'tag': 'institucional',
        }
        payload.update(overrides)
        return payload

    def test_anonymous_cannot_list(self):
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_can_list_but_not_create(self):
        student = StudentFactory()
        self.client.force_authenticate(user=student.user)
        self.assertEqual(self.client.get(LIST_URL).status_code, status.HTTP_200_OK)
        response = self.client.post(LIST_URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_create(self):
        teacher = TeacherFactory()
        self.client.force_authenticate(user=teacher.user)
        response = self.client.post(LIST_URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_secretary_cannot_create(self):
        secretary_admin = SecretaryStaffFactory().user
        self.client.force_authenticate(user=secretary_admin)
        response = self.client.post(LIST_URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dept_admin_create_auto_assigns_department(self):
        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.post(LIST_URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        post = News.objects.get(id=response.data['id'])
        self.assertEqual(post.department_id, self.dept.id)
        self.assertEqual(response.data['department']['name'], self.dept.name)

    def test_dept_admin_cannot_override_department(self):
        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.post(LIST_URL, self._payload(department_id=self.other_dept.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = News.objects.get(id=response.data['id'])
        self.assertEqual(post.department_id, self.dept.id)

    def test_super_admin_can_create_without_department(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(LIST_URL, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = News.objects.get(id=response.data['id'])
        self.assertIsNone(post.department_id)
        self.assertIsNone(response.data['department'])

    def test_super_admin_can_create_with_department(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.post(LIST_URL, self._payload(department_id=self.dept.id), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = News.objects.get(id=response.data['id'])
        self.assertEqual(post.department_id, self.dept.id)

    def test_dept_admin_cannot_edit_other_departments_post(self):
        self.client.force_authenticate(user=self.other_dept_admin)
        response = self.client.post(LIST_URL, self._payload(title='De Matematica'), format='json')
        other_post_id = response.data['id']

        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.patch(_detail_url(other_post_id), {'title': 'Editado'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dept_admin_can_edit_own_post(self):
        self.client.force_authenticate(user=self.dept_admin)
        create = self.client.post(LIST_URL, self._payload(), format='json')
        post_id = create.data['id']

        response = self.client.patch(_detail_url(post_id), {'title': 'Actualizada'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Actualizada')

    def test_super_admin_can_delete_any_post(self):
        self.client.force_authenticate(user=self.dept_admin)
        create = self.client.post(LIST_URL, self._payload(), format='json')
        post_id = create.data['id']

        self.client.force_authenticate(user=self.super_admin)
        response = self.client.delete(_detail_url(post_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(News.objects.filter(id=post_id).exists())

    def test_dept_admin_cannot_delete_other_departments_post(self):
        self.client.force_authenticate(user=self.other_dept_admin)
        create = self.client.post(LIST_URL, self._payload(), format='json')
        post_id = create.data['id']

        self.client.force_authenticate(user=self.dept_admin)
        response = self.client.delete(_detail_url(post_id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

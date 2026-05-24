from rest_framework import status
from rest_framework.test import APITestCase

from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from tests.factories import (
    AdminUserFactory,
    FormOwnershipGroupFactory,
    FormOwnershipMemberFactory,
    StudentFactory,
)


class FormOwnershipGroupListTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.group = FormOwnershipGroupFactory(name='Grupo A')
        self.uri = '/api/ownership-groups/'

    def test_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [g['name'] for g in response.data]
        self.assertIn('Grupo A', names)

    def test_list_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FormOwnershipGroupCreateTests(APITestCase):
    def setUp(self):
        self.superadmin = AdminUserFactory()
        self.admin = AdminUserFactory(is_superuser=False)
        self.uri = '/api/ownership-groups/'

    def test_create_as_superadmin(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(self.uri, {'name': 'Trámites Electivos'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FormOwnershipGroup.objects.filter(name='Trámites Electivos').exists())

    def test_create_as_non_super_admin_forbidden(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.uri, {'name': 'No permitido'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_duplicate_name_fails(self):
        FormOwnershipGroupFactory(name='Duplicado')
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(self.uri, {'name': 'Duplicado'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_unauthenticated(self):
        response = self.client.post(self.uri, {'name': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_with_members_but_no_editor_returns_400(self):
        """A payload that lists members but none has is_editor=True must be rejected."""
        from tests.factories import DepartmentFactory
        dept = DepartmentFactory()
        self.client.force_authenticate(user=self.superadmin)
        payload = {
            'name': 'Grupo sin editor',
            'members': [
                {'entity_type': 'department', 'entity_id': dept.id, 'is_editor': False},
            ],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_duplicate_members_returns_400(self):
        """A payload with the same (entity_type, entity_id) pair twice must be rejected."""
        from tests.factories import DepartmentFactory
        dept = DepartmentFactory()
        self.client.force_authenticate(user=self.superadmin)
        payload = {
            'name': 'Grupo con duplicado',
            'members': [
                {'entity_type': 'department', 'entity_id': dept.id, 'is_editor': True},
                {'entity_type': 'department', 'entity_id': dept.id, 'is_editor': False},
            ],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FormOwnershipGroupUpdateTests(APITestCase):
    def setUp(self):
        self.superadmin = AdminUserFactory()
        self.group = FormOwnershipGroupFactory(name='Original')
        self.uri = f'/api/ownership-groups/{self.group.id}/'

    def test_update_as_superadmin(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.put(self.uri, {'name': 'Actualizado'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Actualizado')

    def test_update_not_found(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.put('/api/ownership-groups/99999/', {'name': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FormOwnershipGroupDeleteTests(APITestCase):
    def setUp(self):
        self.superadmin = AdminUserFactory()

    def test_delete_empty_group(self):
        group = FormOwnershipGroupFactory(name='Para borrar')
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(f'/api/ownership-groups/{group.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FormOwnershipGroup.objects.filter(id=group.id).exists())

    def test_delete_group_with_forms_fails(self):
        from tests.factories import FormFactory, FormTypeFactory
        group = FormOwnershipGroupFactory(name='Con formularios')
        form_type = FormTypeFactory(form_type_value='Digital')
        FormFactory(ownership_group=group, form_type=form_type)
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete(f'/api/ownership-groups/{group.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_not_found(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.delete('/api/ownership-groups/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FormOwnershipMemberUniquenessTests(APITestCase):
    def test_duplicate_member_raises_integrity_error(self):
        group = FormOwnershipGroupFactory()
        FormOwnershipMemberFactory(
            group=group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=1,
        )
        with self.assertRaises(Exception):
            FormOwnershipMember.objects.create(
                group=group,
                entity_type=FormOwnershipMember.DEPARTMENT,
                entity_id=1,
                is_editor=True,
            )

    def test_same_entity_id_different_type_is_allowed(self):
        group = FormOwnershipGroupFactory()
        FormOwnershipMemberFactory(
            group=group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=1,
        )
        member2 = FormOwnershipMember.objects.create(
            group=group,
            entity_type=FormOwnershipMember.SECRETARY,
            entity_id=1,
            is_editor=False,
        )
        self.assertIsNotNone(member2.pk)

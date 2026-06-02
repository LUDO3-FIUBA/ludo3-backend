from rest_framework import status
from rest_framework.test import APITestCase

from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from tests.factories import (
    AdminUserFactory,
    DeptStaffFactory,
    FormOwnershipGroupFactory,
    FormOwnershipMemberFactory,
    SecretaryFactory,
    SecretaryStaffFactory,
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
        self.uri = '/api/ownership-groups/'

    def test_create_as_superadmin(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.post(self.uri, {'name': 'Trámites Electivos'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FormOwnershipGroup.objects.filter(name='Trámites Electivos').exists())

    def test_create_as_dept_staff_auto_injects_own_entity(self):
        staff = DeptStaffFactory()
        self.client.force_authenticate(user=staff.user)
        response = self.client.post(self.uri, {'name': 'Mi Grupo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = FormOwnershipGroup.objects.get(name='Mi Grupo')
        member = FormOwnershipMember.objects.get(group=group)
        self.assertEqual(member.entity_type, FormOwnershipMember.DEPARTMENT)
        self.assertEqual(member.entity_id, staff.department_id)
        self.assertTrue(member.is_editor)

    def test_create_as_dept_staff_ignores_members_payload(self):
        """Members payload from non-superadmin is ignored; their entity is always auto-added."""
        from tests.factories import DepartmentFactory
        staff = DeptStaffFactory()
        other_dept = DepartmentFactory()
        self.client.force_authenticate(user=staff.user)
        payload = {
            'name': 'Grupo Payload',
            'members': [{'entity_type': 'department', 'entity_id': other_dept.id, 'is_editor': True}],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = FormOwnershipGroup.objects.get(name='Grupo Payload')
        members = list(FormOwnershipMember.objects.filter(group=group))
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].entity_id, staff.department_id)

    def test_create_as_secretary_staff_includes_subsecretaries(self):
        parent_sec = SecretaryFactory()
        sub1 = SecretaryFactory(parent_secretary=parent_sec)
        sub2 = SecretaryFactory(parent_secretary=parent_sec)
        staff = SecretaryStaffFactory(secretary=parent_sec)
        self.client.force_authenticate(user=staff.user)
        response = self.client.post(self.uri, {'name': 'Grupo Secretaría'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = FormOwnershipGroup.objects.get(name='Grupo Secretaría')
        members = list(FormOwnershipMember.objects.filter(group=group))
        self.assertEqual(len(members), 3)
        entity_ids = {m.entity_id for m in members}
        self.assertIn(parent_sec.id, entity_ids)
        self.assertIn(sub1.id, entity_ids)
        self.assertIn(sub2.id, entity_ids)
        parent_member = next(m for m in members if m.entity_id == parent_sec.id)
        self.assertTrue(parent_member.is_editor)
        for sub_id in (sub1.id, sub2.id):
            sub_member = next(m for m in members if m.entity_id == sub_id)
            self.assertFalse(sub_member.is_editor)

    def test_create_as_secretary_staff_no_subsecretaries(self):
        sec = SecretaryFactory()
        staff = SecretaryStaffFactory(secretary=sec)
        self.client.force_authenticate(user=staff.user)
        response = self.client.post(self.uri, {'name': 'Solo Secretaría'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = FormOwnershipGroup.objects.get(name='Solo Secretaría')
        members = list(FormOwnershipMember.objects.filter(group=group))
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].entity_id, sec.id)
        self.assertTrue(members[0].is_editor)

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


class FormOwnershipGroupRetrieveTests(APITestCase):
    def setUp(self):
        self.superadmin = AdminUserFactory()
        self.staff = DeptStaffFactory()
        self.own_group = FormOwnershipGroupFactory(name='Grupo Propio')
        self.other_group = FormOwnershipGroupFactory(name='Grupo Ajeno')
        FormOwnershipMemberFactory(
            group=self.own_group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.staff.department_id,
        )
        self.student = StudentFactory()

    def test_superadmin_can_retrieve_any_group(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(f'/api/ownership-groups/{self.other_group.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Grupo Ajeno')

    def test_non_superadmin_can_retrieve_own_group(self):
        self.client.force_authenticate(user=self.staff.user)
        response = self.client.get(f'/api/ownership-groups/{self.own_group.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Grupo Propio')

    def test_non_superadmin_cannot_retrieve_foreign_group(self):
        self.client.force_authenticate(user=self.staff.user)
        response = self.client.get(f'/api/ownership-groups/{self.other_group.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_not_found(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get('/api/ownership-groups/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_unauthenticated(self):
        response = self.client.get(f'/api/ownership-groups/{self.own_group.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(f'/api/ownership-groups/{self.own_group.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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

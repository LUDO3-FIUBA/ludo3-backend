from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories import (
    AdminUserFactory,
    DepartmentFactory,
    DeptStaffFactory,
    FormOwnershipGroupFactory,
    FormOwnershipMemberFactory,
    StudentFactory,
)
from backend.models.form_ownership import FormOwnershipMember


class DepartmentOwnershipGroupsViewTests(APITestCase):
    def setUp(self):
        self.superadmin = AdminUserFactory()
        self.student = StudentFactory()
        self.department = DepartmentFactory()
        self.group = FormOwnershipGroupFactory(name='Grupo Test')
        self.uri = f'/api/departments/{self.department.id}/ownership-groups/'

    def test_set_memberships_as_superadmin(self):
        self.client.force_authenticate(user=self.superadmin)
        payload = {'groups': [{'group_id': self.group.id, 'is_editor': True}]}
        response = self.client.patch(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            FormOwnershipMember.objects.filter(
                group=self.group,
                entity_type=FormOwnershipMember.DEPARTMENT,
                entity_id=self.department.id,
                is_editor=True,
            ).exists()
        )

    def test_set_memberships_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_memberships_as_dept_admin_forbidden(self):
        staff = DeptStaffFactory(department=self.department)
        self.client.force_authenticate(user=staff.user)
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ownership_groups_exposed_in_detail(self):
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.department.id,
            is_editor=True,
        )
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(f'/api/departments/{self.department.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        groups = response.data.get('ownership_groups', [])
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['group_id'], self.group.id)
        self.assertEqual(groups[0]['group_name'], self.group.name)
        self.assertTrue(groups[0]['is_editor'])

    def test_remove_membership(self):
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.department.id,
            is_editor=False,
        )
        self.client.force_authenticate(user=self.superadmin)
        # Send empty list to remove all memberships.
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            FormOwnershipMember.objects.filter(
                entity_type=FormOwnershipMember.DEPARTMENT,
                entity_id=self.department.id,
            ).exists()
        )

    def test_cannot_remove_sole_editor(self):
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.department.id,
            is_editor=True,
        )
        self.client.force_authenticate(user=self.superadmin)
        # Attempt to remove the only editor.
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_group_returns_400(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.patch(
            self.uri, {'groups': [{'group_id': 99999, 'is_editor': False}]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_is_editor_flag(self):
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.department.id,
            is_editor=False,
        )
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.patch(
            self.uri, {'groups': [{'group_id': self.group.id, 'is_editor': True}]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        member = FormOwnershipMember.objects.get(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.department.id,
        )
        self.assertTrue(member.is_editor)

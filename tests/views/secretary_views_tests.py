from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Secretary
from backend.models.staff import Staff
from backend.models.form_ownership import FormOwnershipMember
from tests.factories import (
    AdminUserFactory,
    SecretaryFactory,
    SecretaryStaffFactory,
    StudentFactory,
    FormOwnershipGroupFactory,
    FormOwnershipMemberFactory,
)


class SecretaryListViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.uri = '/api/secretaries/'

    def test_list_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_as_student(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_returns_top_level_only(self):
        """List endpoint returns only secretaries without a parent."""
        parent = SecretaryFactory(name='Secretaría A')
        SecretaryFactory(name='Subsecretaría A1', parent_secretary=parent)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data]
        self.assertIn('Secretaría A', names)
        self.assertNotIn('Subsecretaría A1', names)

    def test_list_includes_subsecretaries_nested(self):
        """The top-level secretary response includes its subsecretaries."""
        parent = SecretaryFactory(name='Secretaría B')
        child = SecretaryFactory(name='Subsecretaría B1', parent_secretary=parent)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entry = next(item for item in response.data if item['name'] == 'Secretaría B')
        subsec_names = [s['name'] for s in entry['subsecretaries']]
        self.assertIn('Subsecretaría B1', subsec_names)


class SecretaryRetrieveViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.secretary = SecretaryFactory(name='Sec Retrieve')
        self.uri = f'/api/secretaries/{self.secretary.id}/'

    def test_retrieve_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Sec Retrieve')


class SecretaryCreateViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.uri = '/api/secretaries/'

    def test_create_as_superadmin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.uri, {'name': 'Nueva Secretaría', 'location': 'Pabellón II'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Nueva Secretaría')

    def test_create_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post(self.uri, {'name': 'Intento'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_without_name_fails(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.uri, {'location': 'Ninguna'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_subsecretaria(self):
        """Creating a Secretary with a parent_secretary creates a subsecretaría."""
        parent = SecretaryFactory(name='Secretaría Padre')
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.uri, {
            'name': 'Subsecretaría Hija',
            'parent_secretary': parent.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent_secretary'], parent.id)

    def test_cannot_create_sub_subsecretaria(self):
        """A subsecretaría cannot itself be the parent of another subsecretaría."""
        parent = SecretaryFactory(name='Secretaría Padre')
        child = SecretaryFactory(name='Subsecretaría', parent_secretary=parent)
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.uri, {
            'name': 'Sub-subsecretaría',
            'parent_secretary': child.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SecretaryUpdateViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.secretary = SecretaryFactory(name='Sec Update')
        self.uri = f'/api/secretaries/{self.secretary.id}/'

    def test_update_as_superadmin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(self.uri, {'name': 'Sec Actualizada'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.secretary.refresh_from_db()
        self.assertEqual(self.secretary.name, 'Sec Actualizada')

    def test_update_as_non_superadmin_own_secretary(self):
        """A secretary admin can edit their own secretary."""
        staff_record = SecretaryStaffFactory(secretary=self.secretary)
        non_super = staff_record.user
        self.client.force_authenticate(user=non_super)
        response = self.client.patch(self.uri, {'name': 'Sec Admin Update'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_as_non_superadmin_other_secretary_forbidden(self):
        """A secretary admin cannot edit a different secretary."""
        other_sec = SecretaryFactory(name='Otra Sec')
        staff_record = SecretaryStaffFactory(secretary=other_sec)
        non_super = staff_record.user
        self.client.force_authenticate(user=non_super)
        response = self.client.patch(self.uri, {'name': 'Intento'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SecretaryDeleteViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.secretary = SecretaryFactory(name='Sec Delete')
        self.uri = f'/api/secretaries/{self.secretary.id}/'

    def test_delete_as_superadmin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.uri)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Secretary.objects.filter(pk=self.secretary.pk).exists())

    def test_delete_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user if hasattr(self, 'student') else StudentFactory().user)
        response = self.client.delete(self.uri)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SecretaryAdminSignalTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()

    def test_creating_secretary_triggers_admin_user(self):
        """Saving a new Secretary should auto-create an associated Staff/User."""
        initial_staff_count = Staff.objects.count()
        secretary = Secretary.objects.create(name='Sec Signal Test')
        final_staff_count = Staff.objects.count()
        self.assertEqual(final_staff_count, initial_staff_count + 1)
        staff = Staff.objects.get(secretary=secretary)
        self.assertTrue(staff.user.is_staff)
        self.assertFalse(staff.user.is_superuser)

    def test_updating_secretary_does_not_create_duplicate_admin(self):
        """Updating an existing Secretary should NOT create another admin."""
        secretary = Secretary.objects.create(name='Sec No Dup')
        count_after_create = Staff.objects.filter(secretary=secretary).count()
        secretary.name = 'Sec No Dup Updated'
        secretary.save()
        count_after_update = Staff.objects.filter(secretary=secretary).count()
        self.assertEqual(count_after_create, count_after_update)


class SecretaryOwnershipGroupsViewTests(APITestCase):
    def setUp(self):
        self.superadmin = AdminUserFactory()
        self.student = StudentFactory()
        self.secretary = SecretaryFactory(name='Sec OG Test')
        self.group = FormOwnershipGroupFactory(name='Grupo Sec')
        self.uri = f'/api/secretaries/{self.secretary.id}/ownership-groups/'

    def test_set_memberships_as_superadmin(self):
        self.client.force_authenticate(user=self.superadmin)
        payload = {'groups': [{'group_id': self.group.id, 'is_editor': True}]}
        response = self.client.patch(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            FormOwnershipMember.objects.filter(
                group=self.group,
                entity_type=FormOwnershipMember.SECRETARY,
                entity_id=self.secretary.id,
                is_editor=True,
            ).exists()
        )

    def test_set_memberships_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_set_memberships_as_sec_admin_forbidden(self):
        staff = SecretaryStaffFactory(secretary=self.secretary)
        self.client.force_authenticate(user=staff.user)
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ownership_groups_exposed_in_detail(self):
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.SECRETARY,
            entity_id=self.secretary.id,
            is_editor=True,
        )
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.get(f'/api/secretaries/{self.secretary.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        groups = response.data.get('ownership_groups', [])
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['group_id'], self.group.id)
        self.assertEqual(groups[0]['group_name'], self.group.name)
        self.assertTrue(groups[0]['is_editor'])

    def test_cannot_remove_sole_editor(self):
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.SECRETARY,
            entity_id=self.secretary.id,
            is_editor=True,
        )
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.patch(self.uri, {'groups': []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_group_returns_400(self):
        self.client.force_authenticate(user=self.superadmin)
        response = self.client.patch(
            self.uri, {'groups': [{'group_id': 99999, 'is_editor': False}]}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

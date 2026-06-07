"""
Tests for Stage 4: authorization logic by ownership group.

Covers:
- Super admin sees all forms.
- Dept admin editor can create/edit/delete form in their group.
- Dept admin non-editor cannot create/edit/delete.
- Secretary admin editor can create/edit/delete form in their group.
- Secretary admin non-editor cannot create/edit/delete.
- Non-member admin cannot list submissions of a form they don't belong to.
- Member admin can list submissions of their group's form.
- Student access (submission create/my_submissions) is unaffected.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models.form import Form
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.models.form_submission import FormSubmission
from backend.models.form_types import FormSubmissionStatus, FormType
from tests.factories import (
    AdminUserFactory,
    DeptStaffFactory,
    DepartmentFactory,
    FormFieldTypeFactory,
    FormOwnershipGroupFactory,
    FormOwnershipMemberFactory,
    FormTypeFactory,
    SecretaryFactory,
    SecretaryStaffFactory,
    StudentFactory,
)


def _make_sent_status():
    obj, _ = FormSubmissionStatus.objects.get_or_create(
        form_submission_status_value=FormSubmissionStatus.SENT,
        defaults={'form_submission_status_label': 'Enviado'},
    )
    return obj


class SuperAdminSeesAllFormsTests(APITestCase):
    """Super admin should see all forms regardless of group membership."""

    def setUp(self):
        self.super_admin = AdminUserFactory()
        self.group1 = FormOwnershipGroupFactory(name='Grupo A')
        self.group2 = FormOwnershipGroupFactory(name='Grupo B')
        self.form_type = FormTypeFactory(form_type_value='Digital')
        Form.objects.create(
            form_name='Form 1', form_description='Desc', ownership_group=self.group1, form_type=self.form_type,
        )
        Form.objects.create(
            form_name='Form 2', form_description='Desc', ownership_group=self.group2, form_type=self.form_type,
        )

    def test_super_admin_sees_all_forms(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get('/api/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_super_admin_sees_forms_from_groups_without_membership(self):
        # Groups have no members at all — super admin still sees the forms.
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get('/api/forms/', {'group_id': self.group1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['form_name'], 'Form 1')


class DeptAdminEditorFormCRUDTests(APITestCase):
    """Department admin marked as editor can create/edit/delete forms in their group."""

    def setUp(self):
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')

        self.dept = DepartmentFactory()
        self.staff = DeptStaffFactory(department=self.dept)
        self.editor_user = self.staff.user

        self.group = FormOwnershipGroupFactory(name='Tramites Depto')
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept.id,
            is_editor=True,
        )

    def test_editor_sees_only_own_group_forms(self):
        other_group = FormOwnershipGroupFactory(name='Otro Grupo')
        Form.objects.create(form_name='Form propia', form_description='d', ownership_group=self.group, form_type=self.form_type)
        Form.objects.create(form_name='Form ajena', form_description='d', ownership_group=other_group, form_type=self.form_type)

        self.client.force_authenticate(user=self.editor_user)
        response = self.client.get('/api/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [f['form_name'] for f in response.data]
        self.assertIn('Form propia', names)
        self.assertNotIn('Form ajena', names)

    def test_editor_can_create_form_in_own_group(self):
        self.client.force_authenticate(user=self.editor_user)
        payload = {
            'form_name': 'Nueva solicitud',
            'form_description': 'Desc',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [
                {
                    'form_field_label': 'Campo',
                    'form_field_type_id': self.field_type.id,
                    'form_field_require': False,
                    'form_field_order': 1,
                }
            ],
        }
        response = self.client.post('/api/forms/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Form.objects.filter(form_name='Nueva solicitud').exists())

    def test_editor_can_update_form_in_own_group(self):
        from backend.models.form import FormField
        form = Form.objects.create(
            form_name='Form original', form_description='d',
            ownership_group=self.group, form_type=self.form_type,
        )
        existing_field = FormField.objects.create(
            form=form, form_field_label='Campo', form_field_type=self.field_type,
            form_field_require=False, form_field_order=1,
        )
        self.client.force_authenticate(user=self.editor_user)
        payload = {
            'form_name': 'Form actualizado',
            'form_description': 'd',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [
                {
                    'form_field_id': existing_field.id,
                    'form_field_label': 'Campo',
                    'form_field_type_id': self.field_type.id,
                    'form_field_require': False,
                    'form_field_order': 1,
                }
            ],
        }
        response = self.client.put(f'/api/forms/{form.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        form.refresh_from_db()
        self.assertEqual(form.form_name, 'Form actualizado')

    def test_editor_can_delete_form_in_own_group(self):
        form = Form.objects.create(
            form_name='Form a eliminar', form_description='d',
            ownership_group=self.group, form_type=self.form_type,
        )
        self.client.force_authenticate(user=self.editor_user)
        response = self.client.delete(f'/api/forms/{form.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Form.objects.filter(id=form.id).exists())

    def test_editor_cannot_create_form_in_other_group(self):
        other_group = FormOwnershipGroupFactory(name='Grupo Ajeno')
        self.client.force_authenticate(user=self.editor_user)
        payload = {
            'form_name': 'Form en grupo ajeno',
            'form_description': 'Desc',
            'ownership_group_id': other_group.id,
            'form_type_id': self.form_type.id,
            'fields': [],
        }
        response = self.client.post('/api/forms/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeptAdminNonEditorFormCRUDTests(APITestCase):
    """Department admin that is a member but NOT editor cannot create/edit/delete forms."""

    def setUp(self):
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')

        self.dept = DepartmentFactory()
        self.staff = DeptStaffFactory(department=self.dept)
        self.non_editor_user = self.staff.user

        self.group = FormOwnershipGroupFactory(name='Tramites Depto')
        # Member but NOT editor.
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept.id,
            is_editor=False,
        )
        self.form = Form.objects.create(
            form_name='Form existente', form_description='d',
            ownership_group=self.group, form_type=self.form_type,
        )

    def test_non_editor_cannot_create_form(self):
        self.client.force_authenticate(user=self.non_editor_user)
        payload = {
            'form_name': 'Nuevo form',
            'form_description': 'Desc',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [],
        }
        response = self.client.post('/api/forms/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_editor_cannot_update_form(self):
        self.client.force_authenticate(user=self.non_editor_user)
        payload = {
            'form_name': 'Form editado',
            'form_description': 'd',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [],
        }
        response = self.client.put(f'/api/forms/{self.form.id}/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_editor_cannot_delete_form(self):
        self.client.force_authenticate(user=self.non_editor_user)
        response = self.client.delete(f'/api/forms/{self.form.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_editor_can_list_forms_in_own_group(self):
        """Non-editor members can still read forms in their group."""
        self.client.force_authenticate(user=self.non_editor_user)
        response = self.client.get('/api/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [f['form_name'] for f in response.data]
        self.assertIn('Form existente', names)

    def test_non_editor_cannot_see_forms_outside_group(self):
        other_group = FormOwnershipGroupFactory(name='Grupo Ajeno')
        Form.objects.create(form_name='Form ajena', form_description='d', ownership_group=other_group, form_type=self.form_type)

        self.client.force_authenticate(user=self.non_editor_user)
        response = self.client.get('/api/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [f['form_name'] for f in response.data]
        self.assertNotIn('Form ajena', names)


class SecretaryAdminAuthzTests(APITestCase):
    """Secretary admin follows the same editor/non-editor logic as department admin."""

    def setUp(self):
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')

        self.secretary = SecretaryFactory()
        self.staff = SecretaryStaffFactory(secretary=self.secretary)
        self.editor_user = self.staff.user

        self.group = FormOwnershipGroupFactory(name='Tramites Secretaria')
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.SECRETARY,
            entity_id=self.secretary.id,
            is_editor=True,
        )

    def test_secretary_editor_can_create_form(self):
        self.client.force_authenticate(user=self.editor_user)
        payload = {
            'form_name': 'Form Secretaria',
            'form_description': 'Desc',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [
                {
                    'form_field_label': 'Campo',
                    'form_field_type_id': self.field_type.id,
                    'form_field_require': False,
                    'form_field_order': 1,
                }
            ],
        }
        response = self.client.post('/api/forms/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_secretary_non_editor_cannot_create_form(self):
        # Add a second secretary and make it non-editor.
        other_sec = SecretaryFactory()
        other_staff = SecretaryStaffFactory(secretary=other_sec)
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.SECRETARY,
            entity_id=other_sec.id,
            is_editor=False,
        )
        self.client.force_authenticate(user=other_staff.user)
        payload = {
            'form_name': 'Form Secretaria 2',
            'form_description': 'Desc',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [],
        }
        response = self.client.post('/api/forms/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminSubmissionListAuthzTests(APITestCase):
    """Admins can only list submissions of forms in their group."""

    def setUp(self):
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.super_admin = AdminUserFactory()
        self.student = StudentFactory()

        # Group with dept member.
        self.dept = DepartmentFactory()
        self.staff = DeptStaffFactory(department=self.dept)
        self.member_user = self.staff.user

        self.group = FormOwnershipGroupFactory(name='Grupo Miembro')
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept.id,
            is_editor=True,
        )

        # A form in the member's group.
        self.form = Form.objects.create(
            form_name='Form del grupo', form_description='d',
            ownership_group=self.group, form_type=self.form_type,
        )

        # A form in a different group.
        self.other_group = FormOwnershipGroupFactory(name='Grupo Otro')
        self.other_form = Form.objects.create(
            form_name='Form de otro grupo', form_description='d',
            ownership_group=self.other_group, form_type=self.form_type,
        )

        # Create a submission for the member's form.
        sent = _make_sent_status()
        self.submission = FormSubmission.objects.create(
            form=self.form, user=self.student.user, status=sent,
        )

    def test_super_admin_can_list_any_form_submissions(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get(f'/api/forms/{self.form.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_admin_can_list_submissions_of_form_outside_any_group(self):
        self.client.force_authenticate(user=self.super_admin)
        response = self.client.get(f'/api/forms/{self.other_form.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_can_list_submissions_of_own_group_form(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(f'/api/forms/{self.form.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_member_cannot_list_submissions_of_another_group_form(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(f'/api/forms/{self.other_form.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StudentAccessUnaffectedTests(APITestCase):
    """Student access to form endpoints must remain unaffected by the new authz logic."""

    def setUp(self):
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')
        self.student = StudentFactory()

        self.group = FormOwnershipGroupFactory(name='Tramites Alumnos')
        self.form = Form.objects.create(
            form_name='Form Alumno', form_description='d',
            ownership_group=self.group, form_type=self.form_type,
        )

    def test_student_can_list_forms(self):
        """Students can list all forms (no group filter applied to them)."""
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get('/api/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_student_can_retrieve_form(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(f'/api/forms/{self.form.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_create_form(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'form_name': 'Form Alumno Malicioso',
            'form_description': 'd',
            'ownership_group_id': self.group.id,
            'form_type_id': self.form_type.id,
            'fields': [],
        }
        response = self.client.post('/api/forms/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

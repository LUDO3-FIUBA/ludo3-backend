"""
Tests for Stage 5: recipient fields on FormSubmission.

Covers:
- Single-member group: recipient auto-filled; no field required in payload.
- Multi-member group: recipient required; missing → 400.
- Multi-member group: recipient not in group → 400.
- Multi-member group: valid recipient → 201, persisted on submission.
- Non-editor member only sees submissions directed to their entity.
- Only the recipient can change submission status; other member → 403.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models.form import Form, FormField
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.models.form_submission import FormSubmission
from backend.models.form_types import FormFieldType, FormSubmissionStatus, FormType
from tests.factories import (
    AdminUserFactory,
    DepartmentFactory,
    DeptStaffFactory,
    FormFieldTypeFactory,
    FormOwnershipGroupFactory,
    FormOwnershipMemberFactory,
    FormTypeFactory,
    StudentFactory,
)


def _make_sent_status():
    obj, _ = FormSubmissionStatus.objects.get_or_create(
        form_submission_status_value=FormSubmissionStatus.SENT,
        defaults={'form_submission_status_label': 'Enviado'},
    )
    return obj


def _make_pending_approval_status():
    obj, _ = FormSubmissionStatus.objects.get_or_create(
        form_submission_status_value=FormSubmissionStatus.PENDING_APPROVAL,
        defaults={'form_submission_status_label': 'Pendiente de aprobación'},
    )
    return obj


def _make_digital_form(group, form_type, field_type):
    form = Form.objects.create(
        form_name='Solicitud test',
        form_description='Desc',
        ownership_group=group,
        form_type=form_type,
    )
    FormField.objects.create(
        form=form,
        form_field_label='Motivo',
        form_field_type=field_type,
        form_field_require=True,
        form_field_order=1,
    )
    return form


class SingleMemberGroupRecipientAutoFillTests(APITestCase):
    """When a group has exactly one member, the recipient is auto-filled."""

    def setUp(self):
        self.student = StudentFactory()
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')
        self.group = FormOwnershipGroupFactory(name='Solo un miembro')
        self.dept = DepartmentFactory()
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept.id,
            is_editor=True,
        )
        self.form = _make_digital_form(self.group, self.form_type, self.field_type)
        _make_sent_status()

    def test_submit_without_recipient_field_succeeds(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [{'field_id': self.form.fields.first().id, 'answer_value': 'Quiero cambiar carrera'}]
        }
        response = self.client.post(f'/api/forms/{self.form.id}/submissions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sub = FormSubmission.objects.get(form=self.form, user=self.student.user)
        self.assertEqual(sub.recipient_entity_type, FormOwnershipMember.DEPARTMENT)
        self.assertEqual(sub.recipient_entity_id, self.dept.id)

    def test_submit_with_explicit_recipient_ignored_and_auto_filled(self):
        """Even if the client sends a recipient, the single-member is used."""
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [{'field_id': self.form.fields.first().id, 'answer_value': 'Test'}],
            'recipient_entity_type': 'department',
            'recipient_entity_id': self.dept.id,
        }
        response = self.client.post(f'/api/forms/{self.form.id}/submissions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sub = FormSubmission.objects.get(form=self.form, user=self.student.user)
        self.assertEqual(sub.recipient_entity_id, self.dept.id)


class MultiMemberGroupRecipientValidationTests(APITestCase):
    """When a group has multiple members, recipient is required and must be a member."""

    def setUp(self):
        self.student = StudentFactory()
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')
        self.group = FormOwnershipGroupFactory(name='Multidestino')
        self.dept_a = DepartmentFactory()
        self.dept_b = DepartmentFactory()
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept_a.id,
            is_editor=True,
        )
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept_b.id,
            is_editor=False,
        )
        self.form = _make_digital_form(self.group, self.form_type, self.field_type)
        _make_sent_status()

    def test_submit_without_recipient_returns_400(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [{'field_id': self.form.fields.first().id, 'answer_value': 'Pedido'}]
        }
        response = self.client.post(f'/api/forms/{self.form.id}/submissions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_with_recipient_outside_group_returns_400(self):
        outside_dept = DepartmentFactory()
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [{'field_id': self.form.fields.first().id, 'answer_value': 'Pedido'}],
            'recipient_entity_type': 'department',
            'recipient_entity_id': outside_dept.id,
        }
        response = self.client.post(f'/api/forms/{self.form.id}/submissions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_with_valid_recipient_succeeds(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [{'field_id': self.form.fields.first().id, 'answer_value': 'Pedido'}],
            'recipient_entity_type': 'department',
            'recipient_entity_id': self.dept_a.id,
        }
        response = self.client.post(f'/api/forms/{self.form.id}/submissions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sub = FormSubmission.objects.get(form=self.form, user=self.student.user)
        self.assertEqual(sub.recipient_entity_type, 'department')
        self.assertEqual(sub.recipient_entity_id, self.dept_a.id)

    def test_response_payload_includes_recipient_fields(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [{'field_id': self.form.fields.first().id, 'answer_value': 'Pedido'}],
            'recipient_entity_type': 'department',
            'recipient_entity_id': self.dept_b.id,
        }
        response = self.client.post(f'/api/forms/{self.form.id}/submissions/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['recipient_entity_type'], 'department')
        self.assertEqual(response.data['recipient_entity_id'], self.dept_b.id)


class NonEditorMemberSubmissionVisibilityTests(APITestCase):
    """Non-editor members only see submissions directed to their entity."""

    def setUp(self):
        self.student = StudentFactory()
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')
        self.group = FormOwnershipGroupFactory(name='Visibilidad')
        self.dept_editor = DepartmentFactory()
        self.dept_reader = DepartmentFactory()

        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept_editor.id,
            is_editor=True,
        )
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept_reader.id,
            is_editor=False,
        )

        self.form = _make_digital_form(self.group, self.form_type, self.field_type)
        sent = _make_sent_status()

        # Submission directed at editor dept
        self.sub_to_editor = FormSubmission.objects.create(
            form=self.form,
            user=self.student.user,
            status=sent,
            recipient_entity_type=FormOwnershipMember.DEPARTMENT,
            recipient_entity_id=self.dept_editor.id,
        )
        # Submission directed at reader dept
        self.sub_to_reader = FormSubmission.objects.create(
            form=self.form,
            user=self.student.user,
            status=sent,
            recipient_entity_type=FormOwnershipMember.DEPARTMENT,
            recipient_entity_id=self.dept_reader.id,
        )

        self.editor_staff = DeptStaffFactory(department=self.dept_editor)
        self.editor_staff.user.is_superuser = False
        self.editor_staff.user.is_staff = True
        self.editor_staff.user.save()

        self.reader_staff = DeptStaffFactory(department=self.dept_reader)
        self.reader_staff.user.is_superuser = False
        self.reader_staff.user.is_staff = True
        self.reader_staff.user.save()

    def test_editor_sees_all_submissions(self):
        self.client.force_authenticate(user=self.editor_staff.user)
        response = self.client.get(f'/api/forms/{self.form.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {s['submission_id'] for s in response.data}
        self.assertIn(self.sub_to_editor.id, ids)
        self.assertIn(self.sub_to_reader.id, ids)

    def test_non_editor_only_sees_submissions_directed_to_them(self):
        self.client.force_authenticate(user=self.reader_staff.user)
        response = self.client.get(f'/api/forms/{self.form.id}/submissions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {s['submission_id'] for s in response.data}
        self.assertIn(self.sub_to_reader.id, ids)
        self.assertNotIn(self.sub_to_editor.id, ids)


class RecipientOnlyCanChangeStatusTests(APITestCase):
    """Only the designated recipient can change a submission's status."""

    def setUp(self):
        self.student = StudentFactory()
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')
        self.group = FormOwnershipGroupFactory(name='Estado test')
        self.dept_recipient = DepartmentFactory()
        self.dept_other = DepartmentFactory()

        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept_recipient.id,
            is_editor=True,
        )
        FormOwnershipMemberFactory(
            group=self.group,
            entity_type=FormOwnershipMember.DEPARTMENT,
            entity_id=self.dept_other.id,
            is_editor=True,
        )

        self.form = _make_digital_form(self.group, self.form_type, self.field_type)
        sent = _make_sent_status()
        _make_pending_approval_status()

        self.submission = FormSubmission.objects.create(
            form=self.form,
            user=self.student.user,
            status=sent,
            recipient_entity_type=FormOwnershipMember.DEPARTMENT,
            recipient_entity_id=self.dept_recipient.id,
        )

        self.recipient_staff = DeptStaffFactory(department=self.dept_recipient)
        self.recipient_staff.user.is_superuser = False
        self.recipient_staff.user.is_staff = True
        self.recipient_staff.user.save()

        self.other_staff = DeptStaffFactory(department=self.dept_other)
        self.other_staff.user.is_superuser = False
        self.other_staff.user.is_staff = True
        self.other_staff.user.save()

    def test_recipient_can_change_status(self):
        self.client.force_authenticate(user=self.recipient_staff.user)
        response = self.client.patch(
            f'/api/submissions/{self.submission.id}/status/',
            {'status': FormSubmissionStatus.PENDING_APPROVAL},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_recipient_member_cannot_change_status(self):
        self.client.force_authenticate(user=self.other_staff.user)
        response = self.client.patch(
            f'/api/submissions/{self.submission.id}/status/',
            {'status': FormSubmissionStatus.PENDING_APPROVAL},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_admin_can_always_change_status(self):
        super_admin = AdminUserFactory()
        self.client.force_authenticate(user=super_admin)
        response = self.client.patch(
            f'/api/submissions/{self.submission.id}/status/',
            {'status': FormSubmissionStatus.PENDING_APPROVAL},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

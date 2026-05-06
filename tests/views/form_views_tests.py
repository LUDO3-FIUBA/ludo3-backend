from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from backend.models.form import Form, FormDocumentSource, FormField, FormFieldOption
from backend.models.form_submission import FormAnswer, FormSubmission
from backend.models.form_types import FormFieldType, FormProcedureType, FormType
from tests.factories import (
    FormFieldTypeFactory,
    FormProcedureTypeFactory,
    FormTypeFactory,
    AdminUserFactory,
    CatalogFactory,
    CatalogItemFactory,
    FormFactory,
    FormFieldFactory,
    FormFieldOptionFactory,
    FormSubmissionFactory,
    StudentFactory,
    TeacherFactory,
)


class FormProcedureTypeViewTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.procedure_type = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.uri = '/api/form-procedure-types/'

    def test_list_returns_procedure_types(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        values = [item['value'] for item in response.data]
        self.assertIn('Administrativo', values)

    def test_list_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FormFieldTypeViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        FormFieldTypeFactory(form_field_type_value='texto')
        FormFieldTypeFactory(form_field_type_value='numero')
        self.uri = '/api/form-field-types/'

    def test_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        values = [item['value'] for item in response.data]
        self.assertIn('texto', values)
        self.assertIn('numero', values)

    def test_list_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FormListViewTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.procedure1 = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.procedure2 = FormProcedureTypeFactory(form_procedure_value='Exámenes')
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.form1 = Form.objects.create(
            form_name='Form A', form_description='Desc A',
            form_procedure=self.procedure1, form_type=self.form_type,
        )
        self.form2 = Form.objects.create(
            form_name='Form B', form_description='Desc B',
            form_procedure=self.procedure2, form_type=self.form_type,
        )
        self.uri = '/api/forms/'

    def test_list_all_forms(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_filtered_by_procedure(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri, {'procedure_id': self.procedure1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['form_name'], 'Form A')

    def test_list_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FormDetailViewTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.procedure = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type_texto = FormFieldTypeFactory(form_field_type_value='texto')
        self.field_type_options = FormFieldTypeFactory(form_field_type_value='options')
        self.field_type_catalog = FormFieldTypeFactory(form_field_type_value='catalog')

        self.form = Form.objects.create(
            form_name='Test Form', form_description='Desc',
            form_procedure=self.procedure, form_type=self.form_type,
        )
        self.field_texto = FormField.objects.create(
            form=self.form, form_field_label='Nombre',
            form_field_type=self.field_type_texto, form_field_require=True, form_field_order=1,
        )
        self.field_options = FormField.objects.create(
            form=self.form, form_field_label='Turno',
            form_field_type=self.field_type_options, form_field_require=False, form_field_order=2,
        )
        FormFieldOption.objects.create(
            form_field=self.field_options, form_option_value='M', form_option_label='Mañana'
        )

        self.catalog = CatalogFactory(catalog_key='careers', catalog_name='Carreras')
        CatalogItemFactory(catalog=self.catalog, catalog_item_value='1', catalog_item_label='Ing. Civil')
        self.field_catalog = FormField.objects.create(
            form=self.form, form_field_label='Carrera',
            form_field_type=self.field_type_catalog, form_field_require=True,
            form_field_order=3, catalog=self.catalog,
        )

        self.uri = f'/api/forms/{self.form.id}/'

    def test_detail_includes_fields_options_and_catalog(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['form_id'], self.form.id)
        self.assertEqual(data['form_name'], 'Test Form')
        self.assertIsNone(data['document_source'])

        fields = {f['form_field_id']: f for f in data['fields']}

        field_options_data = fields[self.field_options.id]
        self.assertIsNotNone(field_options_data['options'])
        self.assertEqual(len(field_options_data['options']), 1)
        self.assertEqual(field_options_data['options'][0]['form_option_value'], 'M')
        self.assertIsNone(field_options_data['catalog'])

        field_catalog_data = fields[self.field_catalog.id]
        self.assertIsNone(field_catalog_data['options'])
        self.assertIsNotNone(field_catalog_data['catalog'])
        self.assertEqual(field_catalog_data['catalog']['catalog_key'], 'careers')
        self.assertEqual(len(field_catalog_data['catalog']['items']), 1)

    def test_detail_not_found(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get('/api/forms/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FormCreateViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.procedure = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.form_type_digital = FormTypeFactory(form_type_value='Digital')
        self.form_type_doc = FormTypeFactory(form_type_value='Documento')
        self.field_type_texto = FormFieldTypeFactory(form_field_type_value='texto')
        self.field_type_options = FormFieldTypeFactory(form_field_type_value='options')
        self.field_type_adjunto = FormFieldTypeFactory(form_field_type_value='adjunto')
        self.uri = '/api/forms/'

    def test_create_digital_form(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'form_name': 'Solicitud',
            'form_description': 'Una solicitud de prueba',
            'form_procedure_id': self.procedure.id,
            'form_type_id': self.form_type_digital.id,
            'fields': [
                {
                    'form_field_label': 'Motivo',
                    'form_field_type_id': self.field_type_texto.id,
                    'form_field_require': True,
                    'form_field_order': 1,
                }
            ],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Form.objects.filter(form_name='Solicitud').exists())
        self.assertEqual(FormField.objects.filter(form__form_name='Solicitud').count(), 1)

    def test_create_digital_form_with_options_field(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'form_name': 'Con opciones',
            'form_description': 'Desc',
            'form_procedure_id': self.procedure.id,
            'form_type_id': self.form_type_digital.id,
            'fields': [
                {
                    'form_field_label': 'Turno',
                    'form_field_type_id': self.field_type_options.id,
                    'form_field_require': False,
                    'form_field_order': 1,
                    'options': [
                        {'form_option_value': 'M', 'form_option_label': 'Mañana'},
                        {'form_option_value': 'T', 'form_option_label': 'Tarde'},
                    ],
                }
            ],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormFieldOption.objects.filter(form_field__form__form_name='Con opciones').count(), 2)

    def test_create_documento_form(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'form_name': 'Nota al decano',
            'form_description': 'Formulario de documento',
            'form_procedure_id': self.procedure.id,
            'form_type_id': self.form_type_doc.id,
            'document_source': 'https://cms.fi.uba.ar/uploads/nota.pdf',
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        form = Form.objects.get(form_name='Nota al decano')
        self.assertTrue(FormDocumentSource.objects.filter(form=form).exists())
        self.assertTrue(FormField.objects.filter(form=form, form_field_type__form_field_type_value='adjunto').exists())

    def test_create_digital_requires_at_least_one_field(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'form_name': 'Sin campos',
            'form_description': 'Desc',
            'form_procedure_id': self.procedure.id,
            'form_type_id': self.form_type_digital.id,
            'fields': [],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_documento_requires_document_source(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'form_name': 'Sin fuente',
            'form_description': 'Desc',
            'form_procedure_id': self.procedure.id,
            'form_type_id': self.form_type_doc.id,
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post(self.uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_unauthenticated(self):
        response = self.client.post(self.uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_rollback_on_invalid_field_type(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            'form_name': 'Debe fallar',
            'form_description': 'Desc',
            'form_procedure_id': self.procedure.id,
            'form_type_id': self.form_type_digital.id,
            'fields': [
                {
                    'form_field_label': 'Adjunto no permitido',
                    'form_field_type_id': self.field_type_adjunto.id,
                    'form_field_require': False,
                    'form_field_order': 1,
                }
            ],
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Form.objects.filter(form_name='Debe fallar').exists())


class FormDigitalSubmissionTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.admin = AdminUserFactory()
        self.procedure = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.form_type_digital = FormTypeFactory(form_type_value='Digital')
        self.field_type_texto = FormFieldTypeFactory(form_field_type_value='texto')
        self.field_type_numero = FormFieldTypeFactory(form_field_type_value='numero')
        self.field_type_mail = FormFieldTypeFactory(form_field_type_value='mail')
        self.field_type_options = FormFieldTypeFactory(form_field_type_value='options')

        self.form = Form.objects.create(
            form_name='Solicitud digital', form_description='Desc',
            form_procedure=self.procedure, form_type=self.form_type_digital,
        )
        self.field_texto = FormField.objects.create(
            form=self.form, form_field_label='Nombre', form_field_type=self.field_type_texto,
            form_field_require=True, form_field_order=1,
        )
        self.field_numero = FormField.objects.create(
            form=self.form, form_field_label='Legajo', form_field_type=self.field_type_numero,
            form_field_require=False, form_field_order=2,
        )
        self.field_options = FormField.objects.create(
            form=self.form, form_field_label='Turno', form_field_type=self.field_type_options,
            form_field_require=False, form_field_order=3,
        )
        self.option = FormFieldOption.objects.create(
            form_field=self.field_options, form_option_value='M', form_option_label='Mañana'
        )
        self.uri = f'/api/forms/{self.form.id}/submissions/'

    def test_submit_digital_success(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [
                {'field_id': self.field_texto.id, 'answer_value': 'Juan'},
                {'field_id': self.field_numero.id, 'answer_value': '42'},
                {'field_id': self.field_options.id, 'answer_value': str(self.option.id)},
            ]
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FormSubmission.objects.filter(form=self.form, user=self.student.user).exists())
        self.assertEqual(FormAnswer.objects.filter(submission__form=self.form).count(), 3)

    def test_submit_missing_required_field(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {'answers': []}
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_invalid_numero(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [
                {'field_id': self.field_texto.id, 'answer_value': 'Juan'},
                {'field_id': self.field_numero.id, 'answer_value': 'not-a-number'},
            ]
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_invalid_option(self):
        self.client.force_authenticate(user=self.student.user)
        payload = {
            'answers': [
                {'field_id': self.field_texto.id, 'answer_value': 'Juan'},
                {'field_id': self.field_options.id, 'answer_value': '99999'},
            ]
        }
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_as_admin_forbidden(self):
        self.client.force_authenticate(user=self.admin)
        payload = {'answers': [{'field_id': self.field_texto.id, 'answer_value': 'Juan'}]}
        response = self.client.post(self.uri, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submit_unauthenticated(self):
        response = self.client.post(self.uri, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FormDocumentSubmissionTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.procedure = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.form_type_doc = FormTypeFactory(form_type_value='Documento')
        self.field_type_adjunto = FormFieldTypeFactory(form_field_type_value='adjunto')

        self.form = Form.objects.create(
            form_name='Nota al decano', form_description='Desc',
            form_procedure=self.procedure, form_type=self.form_type_doc,
        )
        FormDocumentSource.objects.create(
            form=self.form, form_document_source='https://cms.fi.uba.ar/uploads/nota.pdf'
        )
        FormField.objects.create(
            form=self.form, form_field_label='Adjunto', form_field_type=self.field_type_adjunto,
            form_field_require=True, form_field_order=1,
        )
        self.uri = f'/api/forms/{self.form.id}/submissions/document/'

    def test_submit_document_stub_accepts_file(self):
        self.client.force_authenticate(user=self.student.user)
        file = SimpleUploadedFile('nota.pdf', b'PDF content', content_type='application/pdf')
        response = self.client.post(self.uri, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FormSubmission.objects.filter(form=self.form, user=self.student.user).exists())

    def test_submit_document_without_file(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post(self.uri, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_document_unauthenticated(self):
        response = self.client.post(self.uri, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubmissionListAdminTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.procedure = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.field_type = FormFieldTypeFactory(form_field_type_value='texto')

        self.form = Form.objects.create(
            form_name='Form', form_description='Desc',
            form_procedure=self.procedure, form_type=self.form_type,
        )
        self.field = FormField.objects.create(
            form=self.form, form_field_label='Campo', form_field_type=self.field_type,
            form_field_require=False, form_field_order=1,
        )
        self.submission = FormSubmission.objects.create(form=self.form, user=self.student.user)
        FormAnswer.objects.create(submission=self.submission, field=self.field, answer_value='Hola')

        self.uri = f'/api/forms/{self.form.id}/submissions/'

    def test_list_submissions_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        s = response.data[0]
        self.assertEqual(s['submission_id'], self.submission.id)
        self.assertEqual(s['student_first_name'], self.student.user.first_name)
        self.assertEqual(len(s['answers']), 1)
        self.assertEqual(s['answers'][0]['answer_value'], 'Hola')

    def test_list_submissions_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_submissions_unauthenticated(self):
        response = self.client.get(self.uri)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubmissionDeleteTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.procedure = FormProcedureTypeFactory(form_procedure_value='Administrativo')
        self.form_type = FormTypeFactory(form_type_value='Digital')
        self.form = Form.objects.create(
            form_name='Form', form_description='Desc',
            form_procedure=self.procedure, form_type=self.form_type,
        )
        self.submission = FormSubmission.objects.create(form=self.form, user=self.student.user)

    def test_delete_submission_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/submissions/{self.submission.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FormSubmission.objects.filter(id=self.submission.id).exists())

    def test_delete_submission_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.delete(f'/api/submissions/{self.submission.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_submission_not_found(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete('/api/submissions/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_submission_unauthenticated(self):
        response = self.client.delete(f'/api/submissions/{self.submission.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CatalogViewTests(APITestCase):
    def setUp(self):
        self.admin = AdminUserFactory()
        self.student = StudentFactory()
        self.catalog = CatalogFactory(catalog_key='careers', catalog_name='Carreras de FIUBA')
        CatalogItemFactory(catalog=self.catalog, catalog_item_value='1', catalog_item_label='Ing. Civil', catalog_item_active=True)
        CatalogItemFactory(catalog=self.catalog, catalog_item_value='2', catalog_item_label='Bioingeniería', catalog_item_active=False)

    def test_list_catalogs_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/catalogs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['catalog_key'], 'careers')

    def test_list_catalogs_as_student_forbidden(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get('/api/catalogs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_catalog_items_only_returns_active(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(f'/api/catalogs/{self.catalog.id}/items/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['catalog_item_label'], 'Ing. Civil')

    def test_catalog_items_not_found(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get('/api/catalogs/99999/items/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_catalog_items_unauthenticated(self):
        response = self.client.get(f'/api/catalogs/{self.catalog.id}/items/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

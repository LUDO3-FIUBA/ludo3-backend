from django.core.exceptions import ValidationError
from django.test import TestCase

from backend.models.form_types import FormFieldType
from backend.services.form_service import FormService
from tests.factories import (
    CatalogFactory,
    CatalogItemFactory,
    FormFieldFactory,
    FormFieldOptionFactory,
    FormFieldTypeFactory,
)


class FormServiceTests(TestCase):
    def setUp(self):
        self.service = FormService()
        
    def test_validate_answer_empty_value(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.TEXTO)
        field = FormFieldFactory(form_field_type=field_type)
        # Should not raise exception
        self.service._validate_answer(field, None)
        self.service._validate_answer(field, '')

    def test_validate_answer_numero_valid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.NUMERO)
        field = FormFieldFactory(form_field_type=field_type)
        self.service._validate_answer(field, '123')
        self.service._validate_answer(field, '123.45')
        self.service._validate_answer(field, 123)

    def test_validate_answer_numero_invalid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.NUMERO)
        field = FormFieldFactory(form_field_type=field_type)
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 'abc')

    def test_validate_answer_padron_valid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.PADRON)
        field = FormFieldFactory(form_field_type=field_type)
        self.service._validate_answer(field, '12345')
        self.service._validate_answer(field, '1234567')
        self.service._validate_answer(field, 123456)

    def test_validate_answer_padron_invalid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.PADRON)
        field = FormFieldFactory(form_field_type=field_type)
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, '1234')
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, '12345678')
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, '123a5')

    def test_validate_answer_mail_valid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.MAIL)
        field = FormFieldFactory(form_field_type=field_type)
        self.service._validate_answer(field, 'test@example.com')

    def test_validate_answer_mail_invalid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.MAIL)
        field = FormFieldFactory(form_field_type=field_type)
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 'testexample.com')
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 'test@')
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, '@example.com')

    def test_validate_answer_options_valid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.OPTIONS)
        field = FormFieldFactory(form_field_type=field_type)
        option = FormFieldOptionFactory(form_field=field)
        self.service._validate_answer(field, option.id)
        self.service._validate_answer(field, str(option.id))

    def test_validate_answer_options_invalid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.OPTIONS)
        field = FormFieldFactory(form_field_type=field_type)
        FormFieldOptionFactory(form_field=field)  # just to have some option
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 9999)
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 'abc')

    def test_validate_answer_catalog_valid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.CATALOG)
        catalog = CatalogFactory()
        field = FormFieldFactory(form_field_type=field_type, catalog=catalog)
        item = CatalogItemFactory(catalog=catalog, catalog_item_active=True)
        self.service._validate_answer(field, item.id)
        self.service._validate_answer(field, str(item.id))

    def test_validate_answer_catalog_invalid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.CATALOG)
        catalog = CatalogFactory()
        field = FormFieldFactory(form_field_type=field_type, catalog=catalog)
        
        # Valid item but not for this catalog
        catalog2 = CatalogFactory()
        item2 = CatalogItemFactory(catalog=catalog2, catalog_item_active=True)

        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, item2.id)

        # Inactive item
        item3 = CatalogItemFactory(catalog=catalog, catalog_item_active=False)
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, item3.id)

        # Bad format
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 'abc')

    def test_validate_answer_checkbox_valid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.CHECKBOX)
        field = FormFieldFactory(form_field_type=field_type)
        self.service._validate_answer(field, 'true')
        self.service._validate_answer(field, 'false')
        self.service._validate_answer(field, 'True')
        self.service._validate_answer(field, 'False')
        self.service._validate_answer(field, True)
        self.service._validate_answer(field, False)

    def test_validate_answer_checkbox_invalid(self):
        field_type = FormFieldTypeFactory(form_field_type_value=FormFieldType.CHECKBOX)
        field = FormFieldFactory(form_field_type=field_type)
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, 'yes')
        with self.assertRaises(ValidationError):
            self.service._validate_answer(field, '1')

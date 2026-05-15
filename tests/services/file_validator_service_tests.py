import io
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image
from pypdf import PdfWriter

from backend.services.file_validator_service import FileValidatorService


class FileValidatorServiceTests(SimpleTestCase):
    def _make_image_file(self, image_format="PNG", name="image.png"):
        buffer = io.BytesIO()
        image = Image.new("RGB", (1, 1), color=(255, 0, 0))
        image.save(buffer, format=image_format)
        return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{image_format.lower()}")

    def _make_pdf_file(self, name="document.pdf"):
        buffer = io.BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(buffer)
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="application/pdf")

    def test_validate_image_accepts_allowed_extensions(self):
        valid_files = [
            self._make_image_file(image_format="JPEG", name="photo.jpg"),
            self._make_image_file(image_format="JPEG", name="photo.jpeg"),
            self._make_image_file(image_format="PNG", name="diagram.png"),
            self._make_image_file(image_format="PNG", name="preview.webp"),
        ]

        for uploaded_file in valid_files:
            with self.subTest(uploaded_file.name):
                self.assertTrue(FileValidatorService.validate_image(uploaded_file))

    def test_validate_image_rejects_disallowed_extension_even_if_image_is_valid(self):
        uploaded_file = self._make_image_file(image_format="PNG", name="photo.gif")
        self.assertFalse(FileValidatorService.validate_image(uploaded_file))

    def test_validate_image_rejects_non_image_content(self):
        uploaded_file = SimpleUploadedFile(
            "document.png",
            b"not really an image",
            content_type="image/png",
        )
        self.assertFalse(FileValidatorService.validate_image(uploaded_file))

    def test_validate_image_rejects_oversized_file(self):
        uploaded_file = mock.Mock()
        uploaded_file.name = "photo.png"
        uploaded_file.seek.side_effect = lambda *args, **kwargs: None
        uploaded_file.tell.return_value = FileValidatorService.MAX_IMAGE_SIZE + 1
        uploaded_file.read.return_value = b""

        with self.assertRaises(ValidationError):
            FileValidatorService.validate_image(uploaded_file)

    def test_validate_pdf_accepts_valid_pdf(self):
        uploaded_file = self._make_pdf_file()
        self.assertTrue(FileValidatorService.validate_pdf(uploaded_file))

    def test_validate_pdf_rejects_non_pdf_content(self):
        uploaded_file = SimpleUploadedFile(
            "document.pdf",
            b"not really a pdf",
            content_type="application/pdf",
        )
        self.assertFalse(FileValidatorService.validate_pdf(uploaded_file))

    def test_validate_pdf_rejects_oversized_file(self):
        uploaded_file = mock.Mock()
        uploaded_file.seek.side_effect = lambda *args, **kwargs: None
        uploaded_file.tell.return_value = FileValidatorService.MAX_PDF_SIZE + 1
        uploaded_file.read.return_value = b""

        with self.assertRaises(ValidationError):
            FileValidatorService.validate_pdf(uploaded_file)

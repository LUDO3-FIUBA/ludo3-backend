from django.core.exceptions import ValidationError
from PIL import Image
from pypdf import PdfReader
from pathlib import Path
import uuid


class FileValidatorService:
    MAX_PDF_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

    @staticmethod
    def _get_file_size(file_obj):
        file_obj.seek(0, 2)
        file_size = file_obj.tell()
        file_obj.seek(0)
        return file_size

    @staticmethod
    def validate_pdf(file_obj):
        file_size = FileValidatorService._get_file_size(file_obj)

        if file_size > FileValidatorService.MAX_PDF_SIZE:
            raise ValidationError('El PDF no debe exceder 5MB.')

        try:
            file_obj.seek(0)
            header = file_obj.read(5)
            file_obj.seek(0)

            if header != b'%PDF-':
                return False

            reader = PdfReader(file_obj, strict=True)
            _ = len(reader.pages)
            file_obj.seek(0)

            return True
        except ValidationError:
            raise
        except Exception:
            file_obj.seek(0)
            return False

    @staticmethod
    def validate_image(file_obj):
        file_size = FileValidatorService._get_file_size(file_obj)
        file_name = getattr(file_obj, 'name', '') or ''
        file_extension = Path(file_name).suffix.lower()

        if file_extension not in FileValidatorService.ALLOWED_IMAGE_EXTENSIONS:
            return False

        if file_size > FileValidatorService.MAX_IMAGE_SIZE:
            raise ValidationError('La imagen no debe exceder 2MB.')

        try:
            file_obj.seek(0)
            image = Image.open(file_obj)
            image.verify()
            file_obj.seek(0)
            return True
        except ValidationError:
            raise
        except Exception:
            file_obj.seek(0)
            return False

    @staticmethod
    def prepare_upload_with_unique_name(uploaded_file):
        if not uploaded_file:
            return None, None

        original_filename = Path(uploaded_file.name).name
        suffix = Path(original_filename).suffix
        uploaded_file.name = f"{uuid.uuid4().hex}{suffix}"
        return uploaded_file, original_filename

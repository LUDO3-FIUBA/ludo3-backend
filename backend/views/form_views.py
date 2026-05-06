import datetime
import json
import os
import uuid

from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models.catalog import Catalog, CatalogItem
from backend.models.form import Form
from backend.models.form_submission import FormSubmission
from backend.models.form_types import (
    FormFieldType,
    FormProcedureType,
    FormSubmissionStatus,
    FormType,
)
from backend.models.teacher import Teacher
from backend.permissions import IsAdmin, IsStudent, IsTeacher
from backend.serializers.form_serializer import (
    CatalogItemSerializer,
    CatalogSerializer,
    FormCreateSerializer,
    FormDetailSerializer,
    FormFieldTypeSerializer,
    FormListSerializer,
    FormProcedureTypeSerializer,
    FormSubmissionListSerializer,
    FormSubmissionStatusSerializer,
    FormTypeSerializer,
    SubmissionCreateSerializer,
    SubmissionStatusUpdateSerializer,
    TeacherValidationUpdateSerializer,
)
from backend.services.aws_s3_service import get_file_upload_service
from backend.services.form_service import FormService
from backend.views.base_view import BaseViewSet

_ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx'}


def _safe_ext(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return ext if ext in _ALLOWED_EXTENSIONS else ''


def _maybe_upload_template(request, data):
    """If the request includes a `document_source_file`, upload it to S3 and
    inject the resulting URL into `data['document_source']`. Returns mutated data.
    Falls through unchanged if only a URL was sent (CMS link, backward compat)."""
    file_obj = request.FILES.get('document_source_file')
    if file_obj is None:
        return data
    key = f"models/{uuid.uuid4().hex}{_safe_ext(file_obj.name)}"
    url = get_file_upload_service().upload_object(file_obj, key)
    mutable = data.copy() if hasattr(data, 'copy') else dict(data)
    mutable['document_source'] = url
    return mutable


def _resolve_teacher(request, form):
    """Extract and validate teacher_id from request if form requires teacher validation.
    Returns (teacher, error_response) — one will always be None."""
    if not form.requires_teacher_validation:
        return None, None
    teacher_id_raw = request.data.get('teacher_id')
    if not teacher_id_raw:
        return None, Response(
            {'teacher_id': ['Este formulario requiere la selección de un docente validador.']},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        return Teacher.objects.get(pk=int(teacher_id_raw)), None
    except (Teacher.DoesNotExist, ValueError, TypeError):
        return None, Response(
            {'teacher_id': ['Docente no encontrado.']},
            status=status.HTTP_400_BAD_REQUEST,
        )


def _fetch_submission_full(pk):
    return (
        FormSubmission.objects
        .select_related('form', 'user__student', 'status', 'teacher__user')
        .prefetch_related('answers__field')
        .get(pk=pk)
    )


class FormTypeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FormType.objects.all()

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Lista los tipos de formulario")
    def list(self, request):
        return Response(FormTypeSerializer(self.get_queryset(), many=True).data)


class FormProcedureTypeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FormProcedureType.objects.all()

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Lista los tipos de trámite")
    def list(self, request):
        return Response(FormProcedureTypeSerializer(self.get_queryset(), many=True).data)


class FormFieldTypeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = FormFieldType.objects.all()

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Lista los tipos de campo disponibles")
    def list(self, request):
        return Response(FormFieldTypeSerializer(self.get_queryset(), many=True).data)


class FormViewSet(BaseViewSet):
    queryset = Form.objects.select_related('form_procedure', 'form_type').all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        tags=["Formularios"],
        operation_summary="Lista formularios, opcionalmente filtrados por tipo de trámite",
        manual_parameters=[
            openapi.Parameter('procedure_id', openapi.IN_QUERY, type=openapi.FORMAT_INT64,
                              description="ID del tipo de trámite")
        ],
    )
    def list(self, request):
        qs = self.get_queryset()
        procedure_id = request.query_params.get('procedure_id')
        if procedure_id:
            qs = qs.filter(form_procedure_id=procedure_id)
        return Response(FormListSerializer(qs, many=True).data)

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Detalle de un formulario con sus campos")
    def retrieve(self, request, pk=None):
        try:
            form = self.get_queryset().prefetch_related(
                'fields__form_field_type',
                'fields__options',
                'fields__catalog__items',
            ).get(pk=pk)
        except Form.DoesNotExist:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FormDetailSerializer(form).data)

    @swagger_auto_schema(
        tags=["Formularios"],
        operation_summary="Crea un nuevo formulario (transaccional). Acepta multipart con `document_source_file`.",
        request_body=FormCreateSerializer,
    )
    def create(self, request):
        data = _maybe_upload_template(request, request.data)
        serializer = FormCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            form = FormService().create_form(serializer.validated_data)
        except ValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else e.messages,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(FormDetailSerializer(form).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["Formularios"],
        operation_summary="Edita un formulario existente (admin)",
        request_body=FormCreateSerializer,
    )
    def update(self, request, pk=None):
        try:
            form = self.get_queryset().get(pk=pk)
        except Form.DoesNotExist:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        data = _maybe_upload_template(request, request.data)
        serializer = FormCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated_form = FormService().update_form(form, serializer.validated_data)
        except ValidationError as e:
            return Response(
                e.message_dict if hasattr(e, 'message_dict') else e.messages,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(FormDetailSerializer(updated_form).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated], url_path='presign-document')
    @swagger_auto_schema(
        tags=["Formularios"],
        operation_summary="Genera una URL prefirmada para descargar un documento de formulario",
        manual_parameters=[
            openapi.Parameter('url', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="URL del documento a prefirmar")
        ],
    )
    def presign_document(self, request):
        url = request.query_params.get('url')
        if not url:
            return Response({'detail': 'El parámetro url es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)
        presigned = get_file_upload_service().presign_url(url)
        if not presigned:
            return Response({'detail': 'No se pudo generar la URL prefirmada.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'url': presigned})

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Elimina un formulario (admin)")
    def destroy(self, request, pk=None):
        try:
            form = self.get_queryset().get(pk=pk)
        except Form.DoesNotExist:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FormSubmissionViewSet(BaseViewSet):
    """
    Handles operations for form submissions, nested under /forms/{form_pk}/submissions/.
    Includes specific permission logic where listing all submissions is restricted to
    admins, while creating or viewing own submissions requires student access.
    """

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsStudent()]

    def _get_form(self, form_pk):
        try:
            return Form.objects.get(pk=form_pk)
        except Form.DoesNotExist:
            return None

    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Lista todas las respuestas de un formulario (admin)",
    )
    def list(self, request, form_pk=None):
        form = self._get_form(form_pk)
        if not form:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        submissions = (
            FormSubmission.objects
            .filter(form=form)
            .select_related('form', 'user__student', 'status', 'teacher__user')
            .prefetch_related('answers__field')
            .order_by('-submitted_at')
        )
        return Response(FormSubmissionListSerializer(submissions, many=True).data)

    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Envía respuestas a un formulario digital (alumno)",
        request_body=SubmissionCreateSerializer,
    )
    def create(self, request, form_pk=None):
        form = self._get_form(form_pk)
        if not form:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        teacher, err = _resolve_teacher(request, form)
        if err:
            return err

        # Multipart requests send `answers` as a JSON string; parse it back.
        raw_answers = request.data.get('answers')
        if isinstance(raw_answers, str):
            try:
                parsed = json.loads(raw_answers)
            except json.JSONDecodeError:
                return Response({'answers': ['Formato de respuestas inválido.']}, status=status.HTTP_400_BAD_REQUEST)
            data_for_serializer = {'answers': parsed}
        else:
            data_for_serializer = request.data

        serializer = SubmissionCreateSerializer(data=data_for_serializer)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        answers_data = list(serializer.validated_data['answers'])

        # Handle adjunto file upload for digital forms with an adjunto field.
        file_obj = request.FILES.get('file')
        if file_obj:
            adjunto_field = form.fields.filter(
                form_field_type__form_field_type_value='adjunto',
            ).first()
            if adjunto_field is None:
                return Response(
                    {'detail': 'Este formulario no tiene un campo de tipo adjunto.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            padron = request.user.student.padron if hasattr(request.user, 'student') else 'unknown'
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            key = f"submissions/{form.id}/{padron}_{timestamp}_{uuid.uuid4().hex}{_safe_ext(file_obj.name)}"
            url = get_file_upload_service().upload_object(file_obj, key)
            existing = next((a for a in answers_data if a['field_id'] == adjunto_field.id), None)
            if existing:
                existing['answer_value'] = url
            else:
                answers_data.append({'field_id': adjunto_field.id, 'answer_value': url})

        try:
            submission = FormService().create_digital_submission(
                form=form,
                user=request.user,
                answers_data=answers_data,
                teacher=teacher,
            )
        except ValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else e.messages,
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(FormSubmissionListSerializer(_fetch_submission_full(submission.pk)).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated, IsStudent],
            parser_classes=[MultiPartParser, FormParser])
    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Envía un formulario tipo Documento (alumno) — guarda el archivo en data/submissions/",
    )
    def document(self, request, form_pk=None):
        form = self._get_form(form_pk)
        if not form:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if form.form_type.form_type_value != 'Documento':
            return Response({'detail': 'Este formulario no es de tipo Documento.'}, status=status.HTTP_400_BAD_REQUEST)

        teacher, err = _resolve_teacher(request, form)
        if err:
            return err

        file_obj = request.FILES.get('file')
        if file_obj is None:
            return Response({'file': ['Este campo es obligatorio.']}, status=status.HTTP_400_BAD_REQUEST)

        adjunto_field = form.fields.filter(form_field_type__form_field_type_value='adjunto').first()
        if adjunto_field is None:
            return Response(
                {'detail': 'El formulario no tiene un campo de tipo adjunto.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        padron = request.user.student.padron if request.user.is_student else 'unknown'
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        key = f"submissions/{form.id}/{padron}_{timestamp}_{uuid.uuid4().hex}{_safe_ext(file_obj.name)}"
        url = get_file_upload_service().upload_object(file_obj, key)

        sent_status = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.SENT,
        )
        submission = FormSubmission.objects.create(
            form=form,
            user=request.user,
            status=sent_status,
            teacher=teacher,
            teacher_status=FormSubmission.TEACHER_STATUS_PENDING if teacher else None,
        )
        from backend.models.form_submission import FormAnswer  # local import avoids circular ref
        FormAnswer.objects.create(submission=submission, field=adjunto_field, answer_value=url)

        return Response(FormSubmissionListSerializer(_fetch_submission_full(submission.pk)).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Lista las respuestas del usuario autenticado para este formulario",
    )
    def my_submissions(self, request, form_pk=None):
        form = self._get_form(form_pk)
        if not form:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        submissions = (
            FormSubmission.objects
            .filter(form=form, user=request.user)
            .select_related('form', 'user__student', 'status', 'teacher__user')
            .prefetch_related('answers__field')
            .order_by('-submitted_at')
        )
        return Response(FormSubmissionListSerializer(submissions, many=True).data)


class SubmissionAdminViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = FormSubmission.objects.all()

    @swagger_auto_schema(tags=["Formularios — Respuestas"], operation_summary="Elimina una respuesta (admin)")
    def destroy(self, request, pk=None):
        try:
            submission = (
                self.get_queryset()
                .prefetch_related('answers__field__form_field_type')
                .get(pk=pk)
            )
        except FormSubmission.DoesNotExist:
            return Response({'detail': 'Respuesta no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        storage = get_file_upload_service()
        for answer in submission.answers.all():
            if (answer.field.form_field_type.form_field_type_value == 'adjunto'
                    and answer.answer_value):
                key = storage.key_from_url(answer.answer_value)
                if key:
                    try:
                        storage.delete_object(key)
                    except Exception:
                        pass

        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['PATCH'], url_path='status')
    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Cambia el estado de una respuesta (admin)",
        request_body=SubmissionStatusUpdateSerializer,
    )
    def update_status(self, request, pk=None):
        try:
            submission = (
                self.get_queryset()
                .select_related('form', 'status', 'user__student', 'teacher__user')
                .prefetch_related('answers__field')
                .get(pk=pk)
            )
        except FormSubmission.DoesNotExist:
            return Response({'detail': 'Respuesta no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubmissionStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_status_value = serializer.validated_data['status']

        if new_status_value == FormSubmissionStatus.APPROVED:
            if (submission.form.requires_teacher_validation and
                    submission.teacher_status != FormSubmission.TEACHER_STATUS_APPROVED):
                return Response(
                    {'detail': 'Esta respuesta requiere aprobación docente antes de poder ser aprobada.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        new_status = FormSubmissionStatus.objects.get(
            form_submission_status_value=new_status_value,
        )
        submission.status = new_status
        submission.save(update_fields=['status'])
        return Response(FormSubmissionListSerializer(submission).data, status=status.HTTP_200_OK)


class TeacherFormSubmissionViewSet(BaseViewSet):
    """Teacher-facing viewset: see and validate form submissions assigned to this teacher."""
    permission_classes = [IsAuthenticated, IsTeacher]

    def _get_queryset(self, request):
        return (
            FormSubmission.objects
            .filter(teacher=request.user.teacher)
            .select_related('form', 'user__student', 'status', 'teacher__user')
            .prefetch_related('answers__field')
            .order_by('-submitted_at')
        )

    @swagger_auto_schema(
        tags=["Formularios — Docente"],
        operation_summary="Lista las respuestas de formularios asignadas al docente autenticado",
    )
    def list(self, request):
        return Response(FormSubmissionListSerializer(self._get_queryset(request), many=True).data)

    @action(detail=True, methods=['PATCH'], url_path='teacher-status')
    @swagger_auto_schema(
        tags=["Formularios — Docente"],
        operation_summary="El docente aprueba o rechaza una respuesta asignada a él",
        request_body=TeacherValidationUpdateSerializer,
    )
    def update_teacher_status(self, request, pk=None):
        try:
            submission = self._get_queryset(request).get(pk=pk)
        except FormSubmission.DoesNotExist:
            return Response({'detail': 'Respuesta no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeacherValidationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        submission.teacher_status = serializer.validated_data['teacher_status']
        submission.teacher_comment = serializer.validated_data.get('teacher_comment', '')
        submission.save(update_fields=['teacher_status', 'teacher_comment'])

        return Response(FormSubmissionListSerializer(self._get_queryset(request).get(pk=pk)).data,
                        status=status.HTTP_200_OK)


class FormSubmissionStatusViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FormSubmissionStatus.objects.all()

    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Lista los estados disponibles para una respuesta",
    )
    def list(self, request):
        return Response(FormSubmissionStatusSerializer(self.get_queryset(), many=True).data)


class CatalogViewSet(BaseViewSet):
    queryset = Catalog.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    @swagger_auto_schema(tags=["Catálogos"], operation_summary="Lista catálogos disponibles (admin)")
    def list(self, request):
        return Response(CatalogSerializer(self.get_queryset(), many=True).data)

    @action(detail=True, methods=['GET'])
    @swagger_auto_schema(tags=["Catálogos"], operation_summary="Items activos de un catálogo")
    def items(self, request, pk=None):
        try:
            catalog = Catalog.objects.get(pk=pk)
        except Catalog.DoesNotExist:
            return Response({'detail': 'Catálogo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        active_items = CatalogItem.objects.filter(catalog=catalog, catalog_item_active=True)
        return Response(CatalogItemSerializer(active_items, many=True).data)

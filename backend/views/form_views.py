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
from backend.models.form_types import FormFieldType, FormProcedureType, FormType
from backend.permissions import IsAdmin, IsStudent
from backend.serializers.form_serializer import (
    CatalogItemSerializer,
    CatalogSerializer,
    FormCreateSerializer,
    FormDetailSerializer,
    FormFieldTypeSerializer,
    FormListSerializer,
    FormProcedureTypeSerializer,
    FormSubmissionListSerializer,
    FormTypeSerializer,
    SubmissionCreateSerializer,
)
from backend.services.form_service import FormService
from backend.services.local_storage_service import LocalStorageService
from backend.views.base_view import BaseViewSet


def _maybe_upload_template(request, data):
    """If the request includes a `document_source_file`, save it locally and
    inject the resulting URL into `data['document_source']`. Returns mutated data.
    Falls through unchanged if only a URL was sent (CMS link, backward compat)."""
    file_obj = request.FILES.get('document_source_file')
    if file_obj is None:
        return data
    filename = LocalStorageService.upload(file_obj, LocalStorageService.MODELS)
    mutable = data.copy() if hasattr(data, 'copy') else dict(data)
    mutable['document_source'] = LocalStorageService.absolute_url(
        request, LocalStorageService.MODELS, filename,
    )
    return mutable


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

    parser_classes = [JSONParser, MultiPartParser, FormParser]

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

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Elimina un formulario (admin)")
    def destroy(self, request, pk=None):
        try:
            form = self.get_queryset().get(pk=pk)
        except Form.DoesNotExist:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FormSubmissionViewSet(BaseViewSet):
    """Nested under /forms/{form_pk}/submissions/"""

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
        submissions = FormSubmission.objects.filter(form=form).select_related('user__student').prefetch_related('answers__field')
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

        serializer = SubmissionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = FormService().create_digital_submission(
                form=form,
                user=request.user,
                answers_data=serializer.validated_data['answers'],
            )
        except ValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else e.messages,
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(FormSubmissionListSerializer(submission).data, status=status.HTTP_201_CREATED)

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

        file_obj = request.FILES.get('file')
        if file_obj is None:
            return Response({'file': ['Este campo es obligatorio.']}, status=status.HTTP_400_BAD_REQUEST)

        adjunto_field = form.fields.filter(form_field_type__form_field_type_value='adjunto').first()
        if adjunto_field is None:
            return Response(
                {'detail': 'El formulario no tiene un campo de tipo adjunto.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename = LocalStorageService.upload(file_obj, LocalStorageService.SUBMISSIONS)
        url = LocalStorageService.absolute_url(request, LocalStorageService.SUBMISSIONS, filename)

        submission = FormSubmission.objects.create(form=form, user=request.user)
        from backend.models.form_submission import FormAnswer
        FormAnswer.objects.create(submission=submission, field=adjunto_field, answer_value=url)

        return Response(FormSubmissionListSerializer(submission).data, status=status.HTTP_201_CREATED)


class SubmissionAdminViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = FormSubmission.objects.all()

    @swagger_auto_schema(tags=["Formularios — Respuestas"], operation_summary="Elimina una respuesta (admin)")
    def destroy(self, request, pk=None):
        try:
            submission = self.get_queryset().get(pk=pk)
        except FormSubmission.DoesNotExist:
            return Response({'detail': 'Respuesta no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

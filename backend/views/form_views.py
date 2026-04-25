from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
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
from backend.views.base_view import BaseViewSet


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
        if self.action == 'create':
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
        operation_summary="Crea un nuevo formulario (transaccional)",
        request_body=FormCreateSerializer,
    )
    def create(self, request):
        serializer = FormCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            form = FormService().create_form(serializer.validated_data)
        except ValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else e.messages,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(FormDetailSerializer(form).data, status=status.HTTP_201_CREATED)


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

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated, IsStudent])
    @swagger_auto_schema(
        tags=["Formularios — Respuestas"],
        operation_summary="Envía un formulario tipo Documento (alumno) — stub",
    )
    def document(self, request, form_pk=None):
        form = self._get_form(form_pk)
        if not form:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if form.form_type.form_type_value != 'Documento':
            return Response({'detail': 'Este formulario no es de tipo Documento.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'file' not in request.FILES:
            return Response({'file': ['Este campo es obligatorio.']}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: integrar Firebase Storage — subir request.FILES['file'] y guardar la URL resultante
        submission = FormSubmission.objects.create(form=form, user=request.user)
        adjunto_field = form.fields.filter(form_field_type__form_field_type_value='adjunto').first()
        if adjunto_field:
            from backend.models.form_submission import FormAnswer
            FormAnswer.objects.create(submission=submission, field=adjunto_field, answer_value=None)

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

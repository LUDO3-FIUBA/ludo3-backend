import datetime
import json
import logging
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
from backend.models.department import Department
from backend.models.form import Form
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.models.secretary import Secretary
from backend.models.form_submission import FormAnswer, FormSubmission
from backend.models.form_types import (
    FormFieldType,
    FormSubmissionStatus,
    FormType,
)
from backend.models.teacher import Teacher
from backend.permissions import (
    IsAdmin,
    IsSuperAdmin,
    IsStudent,
    IsTeacher,
    get_user_ownership_memberships,
)
from backend.serializers.form_serializer import (
    CatalogItemSerializer,
    CatalogSerializer,
    FormCreateSerializer,
    FormDetailSerializer,
    FormFieldTypeSerializer,
    FormListSerializer,
    FormOwnershipGroupSerializer,
    FormSubmissionListSerializer,
    FormSubmissionStatusSerializer,
    FormTypeSerializer,
    SubmissionCreateSerializer,
    SubmissionStatusUpdateSerializer,
    TeacherValidationUpdateSerializer,
)
from backend.services import storage_service
from botocore.exceptions import ClientError
from backend.services.form_service import FormService
from backend.views.base_view import BaseViewSet

logger = logging.getLogger(__name__)

_ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx'}


def _safe_ext(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValueError(f'Extensión no permitida: {ext or "(sin extensión)"}.')
    return ext


def _maybe_upload_template(request, data):
    """If the request includes a `document_source_file`, upload it to S3 and
    inject the resulting URL into `data['document_source']`. Returns mutated data.
    Falls through unchanged if only a URL was sent (CMS link, backward compat)."""
    file_obj = request.FILES.get('document_source_file')
    if file_obj is None:
        return data
    key = f"models/{uuid.uuid4().hex}{_safe_ext(file_obj.name)}"
    url = storage_service.upload_object(file_obj, key)
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


class FormOwnershipGroupViewSet(BaseViewSet):
    queryset = FormOwnershipGroup.objects.all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated(), IsAdmin()]

    @swagger_auto_schema(tags=["Grupos de propiedad"], operation_summary="Lista los grupos de propiedad")
    def list(self, request):
        groups = self.get_queryset()
        data = FormOwnershipGroupSerializer(groups, many=True).data
        # Annotate is_editor for non-super admins so the frontend can conditionally
        # show create/edit/delete actions per group.
        if request.user.is_staff and not request.user.is_superuser:
            memberships = get_user_ownership_memberships(request.user)
            editor_group_ids = set(memberships.filter(is_editor=True).values_list('group_id', flat=True))
            member_group_ids = set(memberships.values_list('group_id', flat=True))
            for item in data:
                gid = item['id']
                if gid in editor_group_ids:
                    item['is_editor'] = True
                elif gid in member_group_ids:
                    item['is_editor'] = False
                # super-admin or student callers: no annotation needed
        elif request.user.is_superuser:
            for item in data:
                item['is_editor'] = True
        return Response(data)

    @swagger_auto_schema(tags=["Grupos de propiedad"], operation_summary="Detalle de un grupo de propiedad")
    def retrieve(self, request, pk=None):
        try:
            group = self.get_queryset().prefetch_related('members').get(pk=pk)
        except FormOwnershipGroup.DoesNotExist:
            return Response({'detail': 'Grupo de propiedad no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        members = list(group.members.all())
        dept_ids = [m.entity_id for m in members if m.entity_type == FormOwnershipMember.DEPARTMENT]
        sec_ids = [m.entity_id for m in members if m.entity_type == FormOwnershipMember.SECRETARY]

        dept_map = {d.id: d.name for d in Department.objects.filter(id__in=dept_ids)}
        sec_map = {
            s.id: {'name': s.name, 'parent_secretary_name': s.parent_secretary.name if s.parent_secretary_id else None}
            for s in Secretary.objects.select_related('parent_secretary').filter(id__in=sec_ids)
        }

        resolved_members = []
        for m in members:
            if m.entity_type == FormOwnershipMember.DEPARTMENT:
                name = dept_map.get(m.entity_id, f'Departamento #{m.entity_id}')
                parent_secretary_name = None
            else:
                sec = sec_map.get(m.entity_id, {})
                name = sec.get('name', f'Secretaría #{m.entity_id}')
                parent_secretary_name = sec.get('parent_secretary_name')
            resolved_members.append({
                'entity_type': m.entity_type,
                'entity_id': m.entity_id,
                'name': name,
                'is_editor': m.is_editor,
                'parent_secretary_name': parent_secretary_name,
            })

        data = FormOwnershipGroupSerializer(group).data
        data['members'] = resolved_members
        return Response(data)

    @swagger_auto_schema(
        tags=["Grupos de propiedad"],
        operation_summary="Lista entidades elegibles como miembros (departamentos y secretarías)",
    )
    @action(detail=False, methods=['get'], url_path='eligible-entities', permission_classes=[IsAuthenticated, IsSuperAdmin])
    def eligible_entities(self, request):
        departments = [
            {'entity_type': FormOwnershipMember.DEPARTMENT, 'entity_id': d.id, 'name': d.name}
            for d in Department.objects.order_by('name')
        ]
        secretaries = [
            {
                'entity_type': FormOwnershipMember.SECRETARY,
                'entity_id': s.id,
                'name': s.name,
                'parent_secretary_name': s.parent_secretary.name if s.parent_secretary_id else None,
            }
            for s in Secretary.objects.select_related('parent_secretary').order_by('name')
        ]
        return Response(sorted(departments + secretaries, key=lambda x: x['name']))

    @swagger_auto_schema(
        tags=["Grupos de propiedad"],
        operation_summary="Crea un grupo de propiedad (superadmin)",
        request_body=FormOwnershipGroupSerializer,
    )
    def create(self, request):
        serializer = FormOwnershipGroupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        members_data = request.data.get('members', [])
        if not isinstance(members_data, list):
            return Response({'members': ['Debe ser una lista.']}, status=status.HTTP_400_BAD_REQUEST)

        valid_entity_types = {FormOwnershipMember.DEPARTMENT, FormOwnershipMember.SECRETARY}
        seen = set()
        for m in members_data:
            et = m.get('entity_type')
            eid = m.get('entity_id')
            if et not in valid_entity_types:
                return Response(
                    {'members': [f'Tipo de entidad inválido: {et}.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            key = (et, eid)
            if key in seen:
                return Response(
                    {'members': ['No puede haber miembros duplicados en el grupo.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seen.add(key)

        if members_data and not any(m.get('is_editor') for m in members_data):
            return Response(
                {'members': ['El grupo debe tener al menos un miembro con rol de editor.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group = FormOwnershipGroup.objects.create(name=serializer.validated_data['name'])
        for m in members_data:
            FormOwnershipMember.objects.create(
                group=group,
                entity_type=m['entity_type'],
                entity_id=m['entity_id'],
                is_editor=bool(m.get('is_editor', False)),
            )
        return Response(FormOwnershipGroupSerializer(group).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=["Grupos de propiedad"],
        operation_summary="Edita un grupo de propiedad (superadmin)",
        request_body=FormOwnershipGroupSerializer,
    )
    def update(self, request, pk=None):
        try:
            group = self.get_queryset().get(pk=pk)
        except FormOwnershipGroup.DoesNotExist:
            return Response({'detail': 'Grupo de propiedad no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormOwnershipGroupSerializer(group, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        members_data = request.data.get('members', [])
        if not isinstance(members_data, list):
            return Response({'members': ['Debe ser una lista.']}, status=status.HTTP_400_BAD_REQUEST)

        valid_entity_types = {FormOwnershipMember.DEPARTMENT, FormOwnershipMember.SECRETARY}
        seen = set()
        for m in members_data:
            et = m.get('entity_type')
            eid = m.get('entity_id')
            if et not in valid_entity_types:
                return Response(
                    {'members': [f'Tipo de entidad inválido: {et}.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            key = (et, eid)
            if key in seen:
                return Response(
                    {'members': ['No puede haber miembros duplicados en el grupo.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seen.add(key)

        if members_data and not any(m.get('is_editor') for m in members_data):
            return Response(
                {'members': ['El grupo debe tener al menos un miembro con rol de editor.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group.name = serializer.validated_data['name']
        group.save(update_fields=['name'])
        group.members.all().delete()
        for m in members_data:
            FormOwnershipMember.objects.create(
                group=group,
                entity_type=m['entity_type'],
                entity_id=m['entity_id'],
                is_editor=bool(m.get('is_editor', False)),
            )
        return Response(FormOwnershipGroupSerializer(group).data)

    @swagger_auto_schema(tags=["Grupos de propiedad"], operation_summary="Elimina un grupo de propiedad (superadmin)")
    def destroy(self, request, pk=None):
        try:
            group = self.get_queryset().get(pk=pk)
        except FormOwnershipGroup.DoesNotExist:
            return Response({'detail': 'Grupo de propiedad no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if group.forms.exists():
            return Response(
                {'detail': 'No se puede eliminar un grupo que tiene formularios asociados.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FormFieldTypeViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = FormFieldType.objects.all()

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Lista los tipos de campo disponibles")
    def list(self, request):
        return Response(FormFieldTypeSerializer(self.get_queryset(), many=True).data)


class FormViewSet(BaseViewSet):
    queryset = Form.objects.select_related('ownership_group', 'form_type').all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def _get_visible_queryset(self, request):
        """
        Returns a queryset of Forms visible to the requesting user:
        - Super admins and unauthenticated/student callers: all forms.
        - Non-super admins: only forms whose ownership_group contains the
          admin's entity as a member.
        """
        qs = self.get_queryset()
        if request.user.is_staff and not request.user.is_superuser:
            memberships = get_user_ownership_memberships(request.user)
            group_ids = memberships.values_list('group_id', flat=True)
            qs = qs.filter(ownership_group_id__in=group_ids)
        return qs

    def _check_editor_for_group(self, request, group_id):
        """Returns True if the user is an editor in the given group (or is super admin)."""
        if request.user.is_superuser:
            return True
        memberships = get_user_ownership_memberships(request.user)
        return memberships.filter(group_id=group_id, is_editor=True).exists()

    @swagger_auto_schema(
        tags=["Formularios"],
        operation_summary="Lista formularios, opcionalmente filtrados por grupo de propiedad",
        manual_parameters=[
            openapi.Parameter('group_id', openapi.IN_QUERY, type=openapi.FORMAT_INT64,
                              description="ID del grupo de propiedad")
        ],
    )
    def list(self, request):
        qs = self._get_visible_queryset(request)
        group_id = request.query_params.get('group_id')
        if group_id:
            qs = qs.filter(ownership_group_id=group_id)
        return Response(FormListSerializer(qs, many=True).data)

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Detalle de un formulario con sus campos")
    def retrieve(self, request, pk=None):
        try:
            form = self.get_queryset().prefetch_related(
                'fields__form_field_type',
                'fields__options',
                'fields__catalog__items',
                'ownership_group__members',
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
        try:
            data = _maybe_upload_template(request, request.data)
        except ValueError as e:
            return Response({'document_source_file': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FormCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        target_group_id = serializer.validated_data.get('ownership_group_id')
        if not self._check_editor_for_group(request, target_group_id):
            return Response(
                {'detail': 'No tenés permiso de editor en este grupo de propiedad.'},
                status=status.HTTP_403_FORBIDDEN,
            )

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
            form = self._get_visible_queryset(request).get(pk=pk)
        except Form.DoesNotExist:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if not self._check_editor_for_group(request, form.ownership_group_id):
            return Response(
                {'detail': 'No tenés permiso de editor en este grupo de propiedad.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            data = _maybe_upload_template(request, request.data)
        except ValueError as e:
            return Response({'document_source_file': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
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
        presigned = storage_service.presign_url(url)
        if not presigned:
            return Response({'detail': 'No se pudo generar la URL prefirmada.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'url': presigned})

    @swagger_auto_schema(tags=["Formularios"], operation_summary="Elimina un formulario (admin)")
    def destroy(self, request, pk=None):
        try:
            form = self._get_visible_queryset(request).get(pk=pk)
        except Form.DoesNotExist:
            return Response({'detail': 'Formulario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if not self._check_editor_for_group(request, form.ownership_group_id):
            return Response(
                {'detail': 'No tenés permiso de editor en este grupo de propiedad.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class FormSubmissionViewSet(BaseViewSet):
    """
    Handles operations for form submissions, nested under /forms/{form_pk}/submissions/.
    Includes specific permission logic where listing all submissions is restricted to
    admins, while creating or viewing own submissions requires any authenticated user.
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

        # Super admins see all submissions; other admins must be a member of the form's group.
        if not request.user.is_superuser:
            memberships = get_user_ownership_memberships(request.user)
            is_member = memberships.filter(group=form.ownership_group).exists()
            if not is_member:
                return Response({'detail': 'No tenés acceso a este formulario.'}, status=status.HTTP_403_FORBIDDEN)

        submissions_qs = (
            FormSubmission.objects
            .filter(form=form)
            .select_related('form', 'user__student', 'status', 'teacher__user')
            .prefetch_related('answers__field')
            .order_by('-submitted_at')
        )

        # Non-editor members can only see submissions directed to their entity.
        if not request.user.is_superuser:
            is_editor = memberships.filter(group=form.ownership_group, is_editor=True).exists()
            if not is_editor:
                member = memberships.filter(group=form.ownership_group).first()
                if member:
                    submissions_qs = submissions_qs.filter(
                        recipient_entity_type=member.entity_type,
                        recipient_entity_id=member.entity_id,
                    )

        return Response(FormSubmissionListSerializer(submissions_qs, many=True).data)

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
            try:
                ext = _safe_ext(file_obj.name)
            except ValueError as e:
                return Response({'file': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
            padron = request.user.student.padron if hasattr(request.user, 'student') else 'unknown'
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            key = f"submissions/{form.id}/{padron}_{timestamp}_{uuid.uuid4().hex}{ext}"
            url = storage_service.upload_object(file_obj, key)
            existing = next((a for a in answers_data if a['field_id'] == adjunto_field.id), None)
            if existing:
                existing['answer_value'] = url
            else:
                answers_data.append({'field_id': adjunto_field.id, 'answer_value': url})

        recipient_entity_type = serializer.validated_data.get('recipient_entity_type') or None
        recipient_entity_id = serializer.validated_data.get('recipient_entity_id')

        try:
            submission = FormService().create_digital_submission(
                form=form,
                user=request.user,
                answers_data=answers_data,
                teacher=teacher,
                recipient_entity_type=recipient_entity_type,
                recipient_entity_id=recipient_entity_id,
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

        try:
            ext = _safe_ext(file_obj.name)
        except ValueError as e:
            return Response({'file': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
        padron = request.user.student.padron if request.user.is_student else 'unknown'
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        key = f"submissions/{form.id}/{padron}_{timestamp}_{uuid.uuid4().hex}{ext}"
        url = storage_service.upload_object(file_obj, key)

        raw_recipient_type = request.data.get('recipient_entity_type') or None
        raw_recipient_id = request.data.get('recipient_entity_id')
        try:
            recipient_entity_id_val = int(raw_recipient_id) if raw_recipient_id is not None else None
        except (ValueError, TypeError):
            recipient_entity_id_val = None

        try:
            resolved_type, resolved_id = FormService._resolve_recipient(
                form, raw_recipient_type, recipient_entity_id_val,
            )
        except ValidationError as e:
            return Response(e.message_dict if hasattr(e, 'message_dict') else e.messages,
                            status=status.HTTP_400_BAD_REQUEST)

        sent_status = FormSubmissionStatus.objects.get(
            form_submission_status_value=FormSubmissionStatus.SENT,
        )
        submission = FormSubmission.objects.create(
            form=form,
            user=request.user,
            status=sent_status,
            teacher=teacher,
            teacher_status=FormSubmission.TEACHER_STATUS_PENDING if teacher else None,
            recipient_entity_type=resolved_type,
            recipient_entity_id=resolved_id,
        )
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

        for answer in submission.answers.all():
            if (answer.field.form_field_type.form_field_type_value == 'adjunto'
                    and answer.answer_value):
                key = storage_service.key_from_url(answer.answer_value)
                if key:
                    try:
                        storage_service.delete_object(key)
                    except ClientError as e:
                        logger.warning('Failed to delete file %s during submission deletion: %s', key, e)

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

        # Only the designated recipient (or super admin) can change the submission status.
        if not request.user.is_superuser and submission.recipient_entity_type and submission.recipient_entity_id:
            memberships = get_user_ownership_memberships(request.user)
            is_recipient = memberships.filter(
                entity_type=submission.recipient_entity_type,
                entity_id=submission.recipient_entity_id,
            ).exists()
            if not is_recipient:
                return Response(
                    {'detail': 'Solo el destinatario de la respuesta puede cambiar su estado.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

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

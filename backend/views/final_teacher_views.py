from datetime import datetime

from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission, Final
from backend.permissions import *
from backend.serializers.final_serializer import (FinalTeacherListSerializer,
                                                  FinalTeacherSerializer)
from backend.services.audit_log_service import AuditLogService
from backend.services.final_service import FinalService
from backend.views.base_view import BaseViewSet
from backend.views.utils import (get_current_semester, get_current_year,
                                 respond, validate_face)


class FinalTeacherViewSet(BaseViewSet):
    queryset = Final.objects.all()
    serializer_class = FinalTeacherSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        tags=["Finals"]
    )
    def list(self, request):
        subject_siu_id = request.query_params['subject_siu_id']
        teacher = request.user.teacher
        finals = self.queryset.filter(subject_siu_id=subject_siu_id).filter(
            Q(teacher=teacher)
            | Q(commissions__teachers=teacher)
            | Q(commissions__chief_teacher=teacher)
        ).distinct()
        return Response(self._paginate(finals, FinalTeacherListSerializer))

    @swagger_auto_schema(
        tags=["Finals"]
    )
    def create(self, request):
        subject_siu_id = request.data['subject_siu_id']
        commission_ids = request.data.get('commission_ids') or []

        if not commission_ids:
            raise ValidationError({'commission_ids': 'Debés elegir al menos una comisión.'})

        commissions = self._validate_commissions_for_final(
            commission_ids, subject_siu_id, request.user.teacher,
        )

        with transaction.atomic():
            final = Final.objects.create(
                subject_siu_id=subject_siu_id,
                subject_name=request.data['subject_name'],
                date=datetime.utcfromtimestamp(request.data['timestamp']),
                teacher=request.user.teacher,
                status=Final.Status.DRAFT,
            )
            final.commissions.set(commissions)

        AuditLogService().log(request.user, None, f"Docente creo un final para la materia: {request.data['subject_name']}")

        return respond(self.get_serializer(final), response_status=status.HTTP_201_CREATED)

    def _validate_commissions_for_final(self, commission_ids, subject_siu_id, teacher):
        commissions = list(Commission.objects.filter(id__in=commission_ids))
        if len(commissions) != len(set(commission_ids)):
            raise ValidationError({'commission_ids': 'Alguna de las comisiones no existe.'})

        current_year = get_current_year()
        current_semester = get_current_semester()

        for commission in commissions:
            if int(commission.subject_siu_id) != int(subject_siu_id):
                raise ValidationError(
                    {'commission_ids': f"La comisión {commission.siu_id} no pertenece a la materia indicada."}
                )
            in_current_semester = commission.semesters.filter(
                start_date__year=current_year,
                year_moment=current_semester,
            ).exists()
            if not in_current_semester:
                raise ValidationError(
                    {'commission_ids': f"La comisión {commission.siu_id} no está activa en el semestre actual."}
                )

        if not any(c.chief_teacher_id == teacher.pk for c in commissions):
            raise PermissionDenied(
                "Tenés que ser jefe de cátedra de al menos una de las comisiones elegidas."
            )

        return commissions

    @swagger_auto_schema(
        tags=["Finals"]
    )
    def retrieve(self, request, pk=None):
        return respond(self.get_serializer(get_object_or_404(Final.objects, teacher=request.user.teacher, id=pk)))

    @action(detail=True, methods=['POST'])
    @swagger_auto_schema(
        tags=["Finals"]
    )
    def notify_grades(self, request, pk):
        final = self._get_final(request.user.teacher, pk, Final.Status.PENDING_ACT)
        FinalService().notify_grades(final)
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Finals"]
    )
    @action(detail=True, methods=['POST'])
    def close(self, request, pk):
        final = self._get_final(request.user.teacher, pk, Final.Status.OPEN)
        FinalService().close(final)

        AuditLogService().log(request.user, None, f"Docente cerro las entregas de un final: {final}")

        return respond(self.get_serializer(final))

    @swagger_auto_schema(
        tags=["Finals"]
    )
    @action(detail=True, methods=['PUT'])
    def grade(self, request, pk):
        final = self._get_final(request.user.teacher, pk, Final.Status.PENDING_ACT)
        FinalService().grade(final, request.data['grades'])

        AuditLogService().log(request.user, None, f"Docente corrigió un examen final: {final}")
        
        return respond(self.get_serializer(final))

    @swagger_auto_schema(
        tags=["Finals"]
    )
    @action(detail=True, methods=['POST'])
    def send_act(self, request, pk):
        validate_face(request, request.user.teacher)

        final = self._get_final(request.user.teacher, pk, Final.Status.PENDING_ACT)
        FinalService().send_act(final)

        AuditLogService().log(request.user, None, f"Docente cerro el acta de un final: {final}")

        return respond(self.get_serializer(final))

    @swagger_auto_schema(
        tags=["Finals"]
    )
    def _get_final(self, teacher, pk, status):
        return get_object_or_404(Final.objects, teacher=teacher, id=pk, status=status)

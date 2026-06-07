from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models.semester import Commission, Semester
from backend.permissions import *
from backend.serializers.catedra_calendar_entry_serializer import CatedraCalendarEntrySerializer
from backend.serializers.semester_serializer import (SemesterPostSerializer,
                                                     SemesterSerializer)
from backend.serializers.student_serializer import StudentSerializer
from backend.views.base_view import BaseViewSet
from backend.views.utils import teacher_not_in_commission_staff


class SemesterDetailTeacherViews(BaseViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterPostSerializer
    permission_classes = [IsAuthenticated, IsTeacher]

    @action(detail=True, methods=['GET'])
    @swagger_auto_schema(
        tags=["Semesters Teacher"],
        operation_summary="List students enrolled in a particular semester"
    )
    def students(self, request, pk=None):
        semester = get_object_or_404(self.queryset, id=pk)
        teacher = request.user.teacher

        commission = semester.commission
        if teacher_not_in_commission_staff(teacher, commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        return Response(StudentSerializer(semester.students, many=True).data, status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Semesters"],
        operation_summary="Create a semester"
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        commission = get_object_or_404(Commission, id=validated_data['commission'])
        start_date = validated_data['start_date']
        year_moment = validated_data['year_moment']
        classes_amount = validated_data['classes_amount']
        minimum_attendance = validated_data['minimum_attendance']

        if commission.chief_teacher != request.user.teacher:
            return Response("Teacher not chief teacher in commission", status=status.HTTP_403_FORBIDDEN)

        semesters_in_commission = Semester.objects.filter(commission=commission).all()

        already_exists = False
        for semester in semesters_in_commission:
            if (semester.start_date.year == start_date.year and
                year_moment == semester.year_moment):
                already_exists = True

        if already_exists:
            return Response("Semester already exists", status=status.HTTP_403_FORBIDDEN)
        
        semester = Semester(
            commission=commission,
            year_moment=year_moment,
            start_date=start_date,
            classes_amount=classes_amount,
            minimum_attendance=minimum_attendance
        )

        semester.save()
        
        return Response(SemesterSerializer(semester, many=False).data, status.HTTP_200_OK)

    @action(detail=False, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Semesters"],
        operation_summary="Updates a semester"
    )
    def update_semester(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        commission = get_object_or_404(Commission, id=validated_data['commission'])
        start_date = validated_data['start_date']
        year_moment = validated_data['year_moment']
        classes_amount = validated_data['classes_amount']
        minimum_attendance = validated_data['minimum_attendance']

        if commission.chief_teacher != request.user.teacher:
            return Response("Teacher not chief teacher in commission", status=status.HTTP_403_FORBIDDEN)

        semesters_in_commission = Semester.objects.filter(commission=commission).all()

        semester = None
        for a_semester in semesters_in_commission:
            if (a_semester.start_date.year == start_date.year and
                year_moment == a_semester.year_moment):
                semester = a_semester

        if not semester:
            return Response("Semester not found", status=status.HTTP_404_NOT_FOUND)
        
        semester.classes_amount = classes_amount
        semester.minimum_attendance = minimum_attendance

        semester.start_date = start_date

        semester.save()

        return Response(SemesterSerializer(semester, many=False).data, status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Semesters Teacher"],
        operation_summary="Save or update the cátedra calendar source URL for a semester",
    )
    def set_calendar_url(self, request, pk=None):
        semester = get_object_or_404(self.queryset, id=pk)
        if teacher_not_in_commission_staff(request.user.teacher, semester.commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        url = request.data.get('url', '').strip()
        if not url:
            return Response({'error': 'url es requerida'}, status=status.HTTP_400_BAD_REQUEST)

        semester.calendar_source_url = url
        semester.save(update_fields=['calendar_source_url'])
        return Response({'calendar_source_url': semester.calendar_source_url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    @swagger_auto_schema(
        tags=["Semesters Teacher"],
        operation_summary="Sync the cátedra calendar from the configured Google Sheets URL",
    )
    def sync_calendar(self, request, pk=None):
        from backend.services.catedra_calendar_sync_service import sync_catedra_calendar

        semester = get_object_or_404(self.queryset, id=pk)
        if teacher_not_in_commission_staff(request.user.teacher, semester.commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        if not semester.calendar_source_url:
            return Response({'error': 'El semestre no tiene URL de calendario configurada'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            count = sync_catedra_calendar(semester)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except EnvironmentError as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({'error': f'Error al sincronizar: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

        entries = semester.catedra_calendar.all()
        return Response({
            'synced': count,
            'entries': CatedraCalendarEntrySerializer(entries, many=True).data,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    @swagger_auto_schema(
        tags=["Semesters Teacher"],
        operation_summary="Get cátedra calendar entries for a semester",
    )
    def catedra_calendar(self, request, pk=None):
        semester = get_object_or_404(self.queryset, id=pk)
        if teacher_not_in_commission_staff(request.user.teacher, semester.commission):
            return Response("Teacher not a member of this semester commission", status=status.HTTP_403_FORBIDDEN)

        entries = semester.catedra_calendar.all()
        return Response(CatedraCalendarEntrySerializer(entries, many=True).data, status=status.HTTP_200_OK)

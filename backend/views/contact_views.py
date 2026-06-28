from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from backend.models import Contact, Notification, Student, UserNotification
from backend.permissions import IsStudent
from backend.serializers.contact_serializer import ContactSerializer, StudentContactSerializer
from backend.views.utils import get_current_semester, get_current_year


def _get_student(request):
    return Student.objects.get(user=request.user)


def _present_inscriptions(student):
    """Accepted inscriptions for the semester currently in progress."""
    return student.commissioninscription_set.filter(
        status='A',
        semester__start_date__year=get_current_year(),
        semester__year_moment=get_current_semester(),
    )


def _contact_queryset(student):
    return Contact.objects.filter(
        Q(from_student=student) | Q(to_student=student)
    ).select_related('from_student__user', 'to_student__user')


class StudentSearchView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(
        tags=["Contacts"],
        operation_summary="Buscar alumnos por nombre o padrón",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Nombre o padrón", type=openapi.TYPE_STRING, required=True),
        ],
    )
    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Response({'detail': 'La búsqueda debe tener al menos 2 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)

        me = _get_student(request)
        results = Student.objects.filter(
            Q(padron__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        ).exclude(user=request.user).select_related('user')[:20]

        return Response(StudentContactSerializer(results, many=True).data)


class ContactViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(
        tags=["Contacts"],
        operation_summary="Listar contactos (aceptados y pendientes)",
    )
    def list(self, request):
        student = _get_student(request)
        contacts = _contact_queryset(student)
        serializer = ContactSerializer(contacts, many=True, context={'student': student})
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=["Contacts"],
        operation_summary="Enviar solicitud de contacto",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['padron'],
            properties={'padron': openapi.Schema(type=openapi.TYPE_STRING)},
        ),
    )
    def create(self, request):
        student = _get_student(request)
        padron = request.data.get('padron', '').strip()

        try:
            target = Student.objects.select_related('user').get(padron=padron)
        except Student.DoesNotExist:
            return Response({'detail': 'Alumno no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if target == student:
            return Response({'detail': 'No podés agregarte a vos mismo.'}, status=status.HTTP_400_BAD_REQUEST)

        exists = Contact.objects.filter(
            Q(from_student=student, to_student=target) |
            Q(from_student=target, to_student=student)
        ).exists()
        if exists:
            return Response({'detail': 'La solicitud ya existe.'}, status=status.HTTP_409_CONFLICT)

        contact = Contact.objects.create(from_student=student, to_student=target)

        sender_name = f"{student.user.first_name} {student.user.last_name}".strip() or student.padron
        notification = Notification.objects.create(
            title='Nueva solicitud de contacto',
            message=f'{sender_name} te envió una solicitud de contacto.',
            sender=student.user,
            action_url='Contacts',
        )
        UserNotification.objects.create(notification=notification, user=target.user)

        return Response(ContactSerializer(contact, context={'student': student}).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["Contacts"], operation_summary="Aceptar solicitud de contacto")
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        student = _get_student(request)
        try:
            contact = Contact.objects.get(pk=pk, to_student=student, status=Contact.Status.PENDING)
        except Contact.DoesNotExist:
            return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        contact.status = Contact.Status.ACCEPTED
        contact.save(update_fields=['status'])
        return Response(ContactSerializer(contact, context={'student': student}).data)

    @swagger_auto_schema(tags=["Contacts"], operation_summary="Eliminar o rechazar contacto")
    def destroy(self, request, pk=None):
        student = _get_student(request)
        try:
            contact = Contact.objects.get(
                Q(from_student=student) | Q(to_student=student), pk=pk
            )
        except Contact.DoesNotExist:
            return Response({'detail': 'Contacto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        tags=["Contacts"],
        operation_summary="Ver materias en curso de un contacto aceptado",
    )
    @action(detail=True, methods=['get'], url_path='subjects')
    def subjects(self, request, pk=None):
        student = _get_student(request)
        try:
            contact = Contact.objects.get(
                Q(from_student=student) | Q(to_student=student),
                pk=pk, status=Contact.Status.ACCEPTED
            )
        except Contact.DoesNotExist:
            return Response({'detail': 'Contacto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        other = contact.to_student if contact.from_student == student else contact.from_student
        inscriptions = _present_inscriptions(other).select_related(
            'semester__commission'
        ).prefetch_related('semester__schedules')

        data = [
            {
                'subject_name': i.semester.commission.subject_name,
                'subject_siu_id': i.semester.commission.subject_siu_id,
                'semester_id': i.semester.id,
                'schedules': [
                    {
                        'day_of_week': s.day_of_week,
                        'start_time': s.start_time.strftime('%H:%M'),
                        'end_time': s.end_time.strftime('%H:%M'),
                    }
                    for s in i.semester.schedules.all()
                ],
            }
            for i in inscriptions
        ]
        return Response(data)

    @swagger_auto_schema(
        tags=["Contacts"],
        operation_summary="Comparar horarios con un contacto aceptado",
    )
    @action(detail=True, methods=['get'], url_path='schedule-comparison')
    def schedule_comparison(self, request, pk=None):
        student = _get_student(request)
        try:
            contact = Contact.objects.get(
                Q(from_student=student) | Q(to_student=student),
                pk=pk, status=Contact.Status.ACCEPTED
            )
        except Contact.DoesNotExist:
            return Response({'detail': 'Contacto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        other = contact.to_student if contact.from_student == student else contact.from_student

        def get_schedule_blocks(s):
            return [
                {
                    'subject_name': i.semester.commission.subject_name,
                    'day_of_week': sc.day_of_week,
                    'start_time': sc.start_time.strftime('%H:%M'),
                    'end_time': sc.end_time.strftime('%H:%M'),
                }
                for i in _present_inscriptions(s)
                    .select_related('semester__commission')
                    .prefetch_related('semester__schedules')
                for sc in i.semester.schedules.all()
            ]

        my_blocks = get_schedule_blocks(student)
        their_blocks = get_schedule_blocks(other)

        # Compute free gaps: windows where neither is in class on the same day
        # Working hours: 08:00-22:00, minimum gap: 30 min
        def to_minutes(t): return int(t[:2]) * 60 + int(t[3:])
        def from_minutes(m): return f"{m // 60:02d}:{m % 60:02d}"

        all_days = sorted({b['day_of_week'] for b in my_blocks + their_blocks})
        gaps = []
        for day in all_days:
            busy = sorted(
                [(to_minutes(b['start_time']), to_minutes(b['end_time']))
                 for b in my_blocks + their_blocks if b['day_of_week'] == day]
            )
            cursor = 8 * 60  # start at 08:00
            for start, end in busy:
                if start - cursor >= 30:
                    gaps.append({'day_of_week': day, 'start_time': from_minutes(cursor), 'end_time': from_minutes(start)})
                cursor = max(cursor, end)
            if 22 * 60 - cursor >= 30:
                gaps.append({'day_of_week': day, 'start_time': from_minutes(cursor), 'end_time': from_minutes(22 * 60)})

        return Response({
            'mine': my_blocks,
            'theirs': their_blocks,
            'free_gaps': gaps,
        })

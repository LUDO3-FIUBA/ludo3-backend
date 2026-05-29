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


def _get_student(request):
    return Student.objects.get(user=request.user)


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
        inscriptions = other.commissioninscription_set.filter(
            status='A'
        ).select_related('semester__commission')

        data = [
            {
                'subject_name': i.semester.commission.subject_name,
                'subject_siu_id': i.semester.commission.subject_siu_id,
                'semester_id': i.semester.id,
            }
            for i in inscriptions
        ]
        return Response(data)

from collections import defaultdict

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from backend.models import Contact, GroupMembership, Student, StudyGroup
from backend.permissions import IsStudent
from backend.serializers.contact_serializer import StudentContactSerializer


def _get_student(request):
    return Student.objects.get(user=request.user)


def _to_min(t): return int(t[:2]) * 60 + int(t[3:])
def _from_min(m): return f"{m // 60:02d}:{m % 60:02d}"


def _get_blocks(student):
    return [
        {
            'padron': student.padron,
            'full_name': f"{student.user.first_name} {student.user.last_name}".strip(),
            'subject_name': i.semester.commission.subject_name,
            'day_of_week': sc.day_of_week,
            'start_time': sc.start_time.strftime('%H:%M'),
            'end_time': sc.end_time.strftime('%H:%M'),
        }
        for i in student.commissioninscription_set.filter(status='A')
            .select_related('semester__commission')
            .prefetch_related('semester__schedules')
        for sc in i.semester.schedules.all()
    ]


def _compute_ranked_gaps(blocks_per_member, min_duration=30):
    """
    For each day, sweep 08:00-22:00 and find windows where the maximum
    number of members are simultaneously free. Returns gaps sorted by
    free_count descending, each annotated with who can and cannot attend.
    """
    # members_info: list of {padron, full_name}
    members = {p: n for p, n, *_ in [(b['padron'], b['full_name']) for b in sum(blocks_per_member.values(), [])]}
    all_padrones = list(blocks_per_member.keys())
    total = len(all_padrones)
    if total == 0:
        return []

    # Build busy intervals per member per day
    busy = defaultdict(lambda: defaultdict(list))  # padron -> day -> [(start, end)]
    all_days = set()
    for padron, blocks in blocks_per_member.items():
        for b in blocks:
            day = b['day_of_week']
            busy[padron][day].append((_to_min(b['start_time']), _to_min(b['end_time'])))
            all_days.add(day)

    def is_busy(padron, day, t):
        return any(s <= t < e for s, e in busy[padron].get(day, []))

    gaps = []
    for day in sorted(all_days):
        STEP = 30
        t = 8 * 60
        end_day = 22 * 60
        seg_start = t
        seg_free = [p for p in all_padrones if not is_busy(p, day, t)]

        while t <= end_day:
            next_free = [p for p in all_padrones if not is_busy(p, day, t)]
            if set(next_free) != set(seg_free) or t == end_day:
                duration = t - seg_start
                if duration >= min_duration and len(seg_free) >= 1:
                    busy_members = [p for p in all_padrones if p not in seg_free]
                    gaps.append({
                        'day_of_week': day,
                        'start_time': _from_min(seg_start),
                        'end_time': _from_min(t),
                        'free_count': len(seg_free),
                        'total_count': total,
                        'free_members': [{'padron': p, 'full_name': members.get(p, p)} for p in seg_free],
                        'busy_members': [{'padron': p, 'full_name': members.get(p, p)} for p in busy_members],
                        'type': 'all' if len(seg_free) == total else 'majority' if len(seg_free) >= total / 2 else 'minority',
                    })
                seg_start = t
                seg_free = next_free
            t += STEP

    # Sort: more free members first, then by time
    gaps.sort(key=lambda g: (-g['free_count'], g['day_of_week'], _to_min(g['start_time'])))
    return gaps


class StudyGroupViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(tags=["StudyGroups"], operation_summary="Listar mis grupos de estudio")
    
    def list(self, request):
        student = _get_student(request)

        qs = (
            StudyGroup.objects.filter(
                Q(creator=student) |
                Q(memberships__student=student)
            )
            .distinct()
            .prefetch_related('memberships__student__user')
        )

        groups = []

        for g in qs:
            memberships = g.memberships.select_related('student__user')
            my_mem = memberships.filter(student=student).first()

            groups.append({
                'id': g.id,
                'name': g.name,
                'created_at': g.created_at,
                'is_creator': g.creator == student,
                'my_status': (
                    'A'
                    if g.creator == student
                    else (my_mem.status if my_mem else None)
                ),
                'member_count': (
                    memberships.filter(
                        status=GroupMembership.Status.ACCEPTED
                    ).count() + 1
                ),
                'members': [
                    {
                        **StudentContactSerializer(mem.student).data,
                        'status': mem.status,
                    }
                    for mem in memberships
                ],
            })

        return Response(groups)

    @swagger_auto_schema(
        tags=["StudyGroups"], operation_summary="Crear grupo de estudio",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, required=['name'],
                                    properties={'name': openapi.Schema(type=openapi.TYPE_STRING)}),
    )
    def create(self, request):
        student = _get_student(request)
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'detail': 'El nombre es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        group = StudyGroup.objects.create(name=name, creator=student)
        return Response({'id': group.id, 'name': group.name, 'created_at': group.created_at}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["StudyGroups"], operation_summary="Invitar contacto al grupo")
    @action(detail=True, methods=['post'], url_path='invite')
    def invite(self, request, pk=None):
        student = _get_student(request)
        group = StudyGroup.objects.filter(pk=pk, creator=student).first()
        if not group:
            return Response({'detail': 'Grupo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        padron = request.data.get('padron', '').strip()
        try:
            target = Student.objects.get(padron=padron)
        except Student.DoesNotExist:
            return Response({'detail': 'Alumno no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if target == student:
            return Response({'detail': 'No podés invitarte a vos mismo.'}, status=status.HTTP_400_BAD_REQUEST)

        is_contact = Contact.objects.filter(
            Q(from_student=student, to_student=target) | Q(from_student=target, to_student=student),
            status=Contact.Status.ACCEPTED,
        ).exists()
        if not is_contact:
            return Response({'detail': 'Solo podés invitar contactos aceptados.'}, status=status.HTTP_400_BAD_REQUEST)

        membership, created = GroupMembership.objects.get_or_create(group=group, student=target)
        if not created:
            return Response({'detail': 'El alumno ya fue invitado.'}, status=status.HTTP_409_CONFLICT)
        return Response({'id': membership.id, 'status': membership.status}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(tags=["StudyGroups"], operation_summary="Aceptar invitación al grupo")
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        student = _get_student(request)
        try:
            membership = GroupMembership.objects.get(group_id=pk, student=student, status=GroupMembership.Status.PENDING)
        except GroupMembership.DoesNotExist:
            return Response({'detail': 'Invitación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        membership.status = GroupMembership.Status.ACCEPTED
        membership.save(update_fields=['status'])
        return Response({'id': membership.id, 'status': membership.status})

    @swagger_auto_schema(tags=["StudyGroups"], operation_summary="Abandonar o rechazar grupo")
    @action(detail=True, methods=['delete'], url_path='leave')
    def leave(self, request, pk=None):
        student = _get_student(request)
        deleted, _ = GroupMembership.objects.filter(group_id=pk, student=student).delete()
        if not deleted:
            return Response({'detail': 'No pertenecés a este grupo.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(tags=["StudyGroups"], operation_summary="Horarios y franjas libres del grupo")
    @action(detail=True, methods=['get'], url_path='schedule')
    def schedule(self, request, pk=None):
        student = _get_student(request)
        group = StudyGroup.objects.filter(
            Q(creator=student) | Q(memberships__student=student, memberships__status=GroupMembership.Status.ACCEPTED),
            pk=pk,
        ).first()
        if not group:
            return Response({'detail': 'Grupo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # All accepted members + creator
        accepted_ids = list(
            GroupMembership.objects.filter(group=group, status=GroupMembership.Status.ACCEPTED)
            .values_list('student_id', flat=True)
        )
        members = Student.objects.filter(
            Q(pk=group.creator_id) | Q(pk__in=accepted_ids)
        ).select_related('user')

        blocks_per_member = {}
        members_info = []
        for m in members:
            blocks = _get_blocks(m)
            blocks_per_member[m.padron] = blocks
            members_info.append({
                'padron': m.padron,
                'full_name': f"{m.user.first_name} {m.user.last_name}".strip(),
                'is_creator': m == group.creator,
                'block_count': len(blocks),
            })

        all_blocks = [b for blocks in blocks_per_member.values() for b in blocks]

        return Response({
            'group_id': group.id,
            'group_name': group.name,
            'members': members_info,
            'blocks': all_blocks,
            'free_gaps': _compute_ranked_gaps(blocks_per_member),
        })

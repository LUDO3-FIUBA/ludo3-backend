from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Commission, Teacher, TeacherRole
from backend.permissions import *
from backend.serializers.teacher_role_serializer import (
    TeacherRolePostSerializer, TeacherRoleSerializer)
from backend.services.audit_log_service import AuditLogService
from backend.views.base_view import BaseViewSet


class TeacherRoleViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = TeacherRole.objects.all()
    serializer_class = TeacherRolePostSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsTeacher()]
    
    @swagger_auto_schema(
        tags=["Commission Teachers"],
        operation_summary="Add a teacher to a commission"
    )
    def create(self, request):

        teacher = get_object_or_404(Teacher.objects, user_id=request.data["teacher"])
        commission = get_object_or_404(Commission.objects, id=request.data["commission"])
        grader_weight = request.data["grader_weight"]

        if(request.user.teacher != commission.chief_teacher):
            return Response("Cannot add teacher in a commission you are not chief in", status=status.HTTP_403_FORBIDDEN)
        
        if(request.user.teacher == teacher):
            return Response("Cannot add yourself as a teacher", status=status.HTTP_403_FORBIDDEN)
        
        teacher_role = self.queryset.filter(teacher=request.data["teacher"]).filter(commission=request.data["commission"]).first()

        if teacher_role:
            return Response("Teacher role already exist", status=status.HTTP_404_NOT_FOUND)

        teacherRole = TeacherRole(teacher=teacher, commission=commission, role=request.data["role"], grader_weight=grader_weight)
        teacherRole.save()
        
        AuditLogService().log(request.user, teacher.user, f"Usuario agregó un nuevo docente a la comisión {commission}")

        return Response(TeacherRoleSerializer(teacherRole).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Commission Teachers"],
        operation_summary="Change a teacher role for a commission"
    )
    def put(self, request):

        commission = get_object_or_404(Commission.objects, id=request.data["commission"])

        if(request.user.teacher != commission.chief_teacher):
            return Response("Cannot change teacher in a commission you are not chief in", status=status.HTTP_403_FORBIDDEN)
        
        teacher_role = self.queryset.filter(teacher=request.data["teacher"]).filter(commission=request.data["commission"]).first()

        if not teacher_role:
            return Response("Teacher role does not exist", status=status.HTTP_404_NOT_FOUND)

        teacher_role.role = request.data["role"]
        teacher_role.grader_weight = request.data["grader_weight"]
        teacher_role.save()
        
        AuditLogService().log(request.user, teacher_role.teacher.user, f"Usuario edito el rol de un docente en la comision {commission}")
        
        return Response(TeacherRoleSerializer(teacher_role).data, status.HTTP_200_OK)
    

    @swagger_auto_schema(
        tags=["Commission Teachers"],
        operation_summary="Gets all teachers for a commission",
        manual_parameters=[
            openapi.Parameter('commission_id', openapi.IN_QUERY, description="Id of commission to get teachers from", type=openapi.FORMAT_INT64)
        ]
    )
    def list(self, request):
        result = TeacherRole.objects.all().filter(commission=request.query_params['commission_id'])
        return Response(TeacherRoleSerializer(result, many=True).data, status.HTTP_200_OK)
    


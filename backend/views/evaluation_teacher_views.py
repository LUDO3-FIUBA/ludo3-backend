from backend.permissions import IsTeacher
from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Evaluation, Semester
from backend.serializers.evaluation_serializer import (
    EvaluationPostSerializer, EvaluationSerializer, EvaluationUpdateSerializer)
from backend.services.evaluation_service import EvaluationService
from backend.services.notification_service import NotificationService
from backend.views.base_view import BaseViewSet
from backend.views.utils import datetime_format, teacher_not_in_commission_staff


class EvaluationTeacherViewSet(BaseViewSet):
    permission_classes = [IsAuthenticated, IsTeacher]
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationPostSerializer
    
    @action(detail=False, methods=['POST'])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Adds an evaluation for a semester"
    )
    def add_evaluation(self, request):
        evaluation_data = request.data
        evaluation_serializer = EvaluationPostSerializer(data=evaluation_data)
        if evaluation_serializer.is_valid():
            semester = self._semester(evaluation_serializer.initial_data["semester_id"])
            if semester.commission.chief_teacher != request.user.teacher:
                return Response("Teacher not chief teacher in commission", status=status.HTTP_403_FORBIDDEN)

            try:
                evaluation = EvaluationService().create(evaluation_serializer.validated_data)
            except ValidationError as e:
                payload = getattr(e, "message_dict", None) or {"detail": e.messages}
                return Response(payload, status=status.HTTP_400_BAD_REQUEST)

            return Response(EvaluationSerializer(evaluation).data, status=status.HTTP_201_CREATED)
        return Response(evaluation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _semester(self, semester_pk):
        return get_object_or_404(Semester.objects, id=semester_pk)
    
    @action(detail=False, methods=['PUT'])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Updates an evaluation for a semester"
    )
    def update_evaluation(self, request):
        evaluation_id = request.data.get("evaluation_id")
        if evaluation_id is None:
            return Response({"evaluation_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        evaluation = get_object_or_404(Evaluation.objects, id=evaluation_id)
        if evaluation.semester.commission.chief_teacher != request.user.teacher:
            return Response("Teacher not chief teacher in commission", status=status.HTTP_403_FORBIDDEN)

        serializer = EvaluationUpdateSerializer(evaluation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            evaluation = EvaluationService().update(evaluation, serializer.validated_data)
        except ValidationError as e:
            payload = getattr(e, "message_dict", None) or {"detail": e.messages}
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(EvaluationSerializer(evaluation).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['DELETE'])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Deletes an evaluation for a semester"
    )
    def delete_evaluation(self, request):
        evaluation_id = request.data.get("evaluation_id")
        if evaluation_id is None:
            return Response({"evaluation_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

        evaluation = get_object_or_404(Evaluation.objects, id=evaluation_id)
        if evaluation.semester.commission.chief_teacher != request.user.teacher:
            return Response("Teacher not chief teacher in commission", status=status.HTTP_403_FORBIDDEN)

        evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Gets all evaluations in a semester",
        manual_parameters=[
            openapi.Parameter('semester', openapi.IN_QUERY, description="Id of semester to get evaluations from", type=openapi.FORMAT_INT64)
        ]
    )
    def get_evaluations(self, request):
        semester = get_object_or_404(Semester.objects, id=request.query_params["semester"])
        
        if teacher_not_in_commission_staff(request.user.teacher, semester.commission):
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        
        evaluations = Evaluation.objects.filter(semester=semester).all()
        return Response(EvaluationSerializer(evaluations, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    @swagger_auto_schema(
        tags=["Evaluations"],
        operation_summary="Notifies grades"
    )
    def notify_grades(self, request, pk=None):

        evaluation = get_object_or_404(Evaluation.objects, id=pk)

        NotificationService().notify_evaluation_grade(evaluation)
        return Response(status=status.HTTP_200_OK)

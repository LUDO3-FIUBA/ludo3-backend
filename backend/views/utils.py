from datetime import datetime

from rest_framework import status
from rest_framework.response import Response

from backend.api_exceptions import FaceRegistrationPendingError, InvalidFaceError
from backend.models.commission import Commission
from backend.models.teacher import Teacher
from backend.models.teacher_role import TeacherRole
from backend.services.image_validator_service import ImageValidatorService
from backend.utils import get_current_datetime, is_before_current_datetime, datetime_format


def respond(result, response_status=status.HTTP_200_OK):
    return respond_plain(result.data, response_status=response_status)


def respond_plain(result, response_status=status.HTTP_200_OK):
    return Response(result, status=response_status)


def serialize(self, relation):
    page = self.paginate_queryset(relation)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    serializer = self.get_serializer(relation, many=True)
    return Response(serializer.data)


def validate_face(request, model):
    if not request.data.get("image"):
        raise InvalidFaceError()

    if not getattr(model, "face_encodings", None):
        raise FaceRegistrationPendingError()

    is_match = ImageValidatorService(request.data["image"]).validate_identity(model)

    if not is_match:
        raise InvalidFaceError()


def get_current_semester():
    mes = datetime.now().month
    # TODO: hacerlo configurable
    if (mes >= 7) or (mes <= 2):
        return "SS"
    return "FS"


def get_current_year():
    return 2024


def get_hours_from_current_time(past_datetime):
    SECONDS_IN_ONE_HOUR = 3600
    return (
        get_current_datetime() - past_datetime
    ).total_seconds() / SECONDS_IN_ONE_HOUR


def get_required_int_query_param(request, param_name):
    value = request.query_params.get(param_name)
    if value is None:
        return None, Response(
            {"detail": f"{param_name} query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, Response(
            {"detail": f"Invalid {param_name}."},
            status=status.HTTP_400_BAD_REQUEST,
        )

def teacher_not_in_commission_staff(teacher: Teacher, commission: Commission) -> bool:
    return (
        teacher not in commission.teachers.all() and commission.chief_teacher != teacher
    )


def get_stub_chief_teacher_role(commission: Commission) -> TeacherRole:
    return TeacherRole(
        commission=commission,
        teacher=commission.chief_teacher,
        grader_weight=commission.chief_teacher_grader_weight,
        role="Profesor Titular",
    )

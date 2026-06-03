from rest_framework.exceptions import APIException
from rest_framework import status


class InvalidImageError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_image'


class ErrorCommunicatingWithExternalSourceError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_code = 'communication_error'


class InvalidDataError(APIException):
    status_code = 422
    default_code = 'invalid_data'


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'invalid_data'


class InvalidFaceError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'invalid_face'


class FaceRegistrationPendingError(APIException):
    status_code = 422
    default_code = 'face_registration_pending'
    default_detail = 'El registro facial del usuario está incompleto.'


class InvalidSubjectCodeError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'invalid_subject_code'


class AttendanceAlreadyValidError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'attendance_already_valid'
    default_detail = 'Ya diste tu presente y fuiste anotado en la planilla.'


class LocationAttendanceWindowExpiredError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'location_attendance_window_expired'
    default_detail = 'Ya pasaron los 10 minutos disponibles para marcar presencia por ubicación.'

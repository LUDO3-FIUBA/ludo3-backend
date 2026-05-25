from .attendance_add_student_to_qr_views import AttendanceAddStudentToQRViewSet
from .attendance_student_views import AttendanceViewSet
from .attendance_teacher_views import AttendanceTeacherViewSet
from .base_view import BaseViewSet
from .commission_inscription_teacher_views import \
    CommissionInscriptionTeacherViewSet
from .commission_teacher_views import CommissionTeacherViewSet
from .commission_views import CommissionViewSet
from .commissionInscription_views import CommissionInscriptionViewSet
from .custom_gcm_device_viewset import CustomGCMDeviceViewSet
from .evaluation_submission_student_views import EvaluationSubmissionViewSet
from .evaluation_submission_download_views import EvaluationSubmissionDownloadView
from .evaluation_submission_teacher_views import \
    EvaluationSubmissionTeacherViewSet
from .evaluation_teacher_views import EvaluationTeacherViewSet
from .evaluation_views import EvaluationViewSet
from .final_exam_student_views import FinalExamStudentViewSet
from .final_exam_teacher_views import FinalExamTeacherViews
from .final_teacher_views import FinalTeacherViewSet
from .semester_detail_teacher_views import SemesterDetailTeacherViews
from .semester_views import SemesterViewSet
from .statistics_student_views import StatisticsStudentViewSet
from .statistics_teacher_views import StatisticsTeacherViewSet
from .student_views import StudentViews
from .subject_views import SubjectViewSet
from .teacher_role_views import TeacherRoleViewSet
from .teacher_views import TeacherViews
from .notification_views import NotificationViewSet
from .notification_admin_views import NotificationAdminViewSet
from .notification_teacher_views import NotificationTeacherViewSet
from .academic_calendar_event_views import AcademicCalendarEventViewSet
from .department_views import DepartmentViewSet
from .news_views import NewsViewSet
from .admin_finals_views import AdminFinalsViewSet
from .commission_admin_views import CommissionAdminViewSet
from .user_admin_views import UserAdminViewSet
from .form_views import (
    FormTypeViewSet,
    FormProcedureTypeViewSet,
    FormFieldTypeViewSet,
    FormSubmissionStatusViewSet,
    FormViewSet,
    FormSubmissionViewSet,
    SubmissionAdminViewSet,
    TeacherFormSubmissionViewSet,
    CatalogViewSet,
)
from .student_identity_views import StudentIdentityViewSet
from .guarani_views import OfertaComisionesView
from .bedelia_views import BedeliaClassroomChangeViewSet

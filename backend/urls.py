from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_nested import routers

from . import views
from .views import CustomGCMDeviceViewSet
from .views.guarani_views import OfertaComisionesView, PlanCarreraView
from .views.user_views import UserCustomViewSet, simple_login
from .views.google_auth_views import google_sign_in, google_complete_registration
from .views.password_views import change_password, forgot_password, reset_password_confirm
from .views.cookie_auth_views import jwt_refresh, jwt_logout

router = routers.SimpleRouter()
router.register(r'final_exams', views.FinalExamStudentViewSet, 'final_exam')
router.register(r'finals', views.FinalTeacherViewSet, 'final')
router.register(r'subjects', views.SubjectViewSet, 'subject')
router.register(r'commissions', views.CommissionViewSet, 'commission')
router.register(r'commissions/teachers', views.TeacherRoleViewSet, 'commission')
router.register(r'teacher/commissions', views.CommissionTeacherViewSet, 'commission')
router.register(r'semesters', views.SemesterViewSet, 'semester')
router.register(r'semesters/attendance', views.AttendanceViewSet, 'attendance')
router.register(r'teacher/semesters', views.SemesterDetailTeacherViews, 'semester')
router.register(r'teacher/semesters/attendance', views.AttendanceTeacherViewSet, 'attendance')
router.register(r'teacher/semesters/attendance/student', views.AttendanceAddStudentToQRViewSet, 'attendance')
router.register(r'evaluations', views.EvaluationViewSet, 'evaluation')
router.register(r'evaluations/submissions', views.EvaluationSubmissionViewSet, 'evaluation')
router.register(r'teacher/evaluations', views.EvaluationTeacherViewSet, 'evaluation')
router.register(r'teacher/evaluations/submissions', views.EvaluationSubmissionTeacherViewSet, 'evaluation')
router.register(r'teachers', views.TeacherViews, 'teachers')
router.register(r'students', views.StudentViews, 'students')
router.register(r'commission_inscription', views.CommissionInscriptionViewSet, 'commission_inscription')
router.register(r'teacher/commission_inscription', views.CommissionInscriptionTeacherViewSet, 'commission_inscription')
router.register(r'statistics/student', views.StatisticsStudentViewSet, 'statistics_student')
router.register(r'statistics/teacher', views.StatisticsTeacherViewSet, 'statistics_teacher')
router.register(r'notifications', views.NotificationViewSet, 'notification')
router.register(r'device/gcm', CustomGCMDeviceViewSet)
router.register(r'academic_calendar', views.AcademicCalendarEventViewSet, 'academic_calendar')
router.register(r'departments', views.DepartmentViewSet, 'department')
router.register(r'news', views.NewsViewSet, 'news')
router.register(r'admin/commissions', views.CommissionAdminViewSet, 'admin-commission')
router.register(r'admin/finals', views.AdminFinalsViewSet, 'admin-final')
router.register(r'admin/users', views.UserAdminViewSet, 'admin-user')
router.register(r'bedelia/classroom-changes', views.BedeliaClassroomChangeViewSet, 'bedelia-classroom-change')
router.register(r'form-types', views.FormTypeViewSet, 'form-type')
router.register(r'form-procedure-types', views.FormProcedureTypeViewSet, 'form-procedure-type')
router.register(r'form-field-types', views.FormFieldTypeViewSet, 'form-field-type')
router.register(r'form-submission-statuses', views.FormSubmissionStatusViewSet, 'form-submission-status')
router.register(r'forms', views.FormViewSet, 'form')
router.register(r'submissions', views.SubmissionAdminViewSet, 'submission')
router.register(r'teacher/form-submissions', views.TeacherFormSubmissionViewSet, 'teacher-form-submission')
router.register(r'catalogs', views.CatalogViewSet, 'catalog')
router.register(r'student_identity', views.StudentIdentityViewSet, 'student-identity')
router.register(r'admin/notifications', views.NotificationAdminViewSet, 'admin-notification')
router.register(r'teacher/notifications', views.NotificationTeacherViewSet, 'teacher-notification')

teacher_finals_router = routers.NestedSimpleRouter(router, r'finals', lookup='final')
teacher_finals_router.register(r'final_exams', views.FinalExamTeacherViews, basename='final-final_exams')

forms_submissions_router = routers.NestedSimpleRouter(router, r'forms', lookup='form')
forms_submissions_router.register(r'submissions', views.FormSubmissionViewSet, basename='form-submissions')

auth_router = routers.DefaultRouter()
auth_router.register(r'auth/users', UserCustomViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="LUDO API",
        default_version='v1',),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # app own routes
    path('api/', include(router.urls)),
    path('api/evaluations/submissions/<int:pk>/download/', views.EvaluationSubmissionDownloadView.as_view(), name='evaluation-submission-download'),
    path('api/', include(teacher_finals_router.urls)),
    path('api/', include(forms_submissions_router.urls)),

    # custom cookie-aware JWT refresh/logout (must come before djoser include)
    path('auth/jwt/refresh/', jwt_refresh, name='jwt-refresh'),
    path('auth/jwt/logout/', jwt_logout, name='jwt-logout'),

    # path to djoser end points
    path('auth/', include('djoser.urls.jwt')),

    path('', include(auth_router.urls)),
    re_path(r'^auth/login/$', simple_login, name='api-login'),
    path('auth/password/change/', change_password, name='password-change'),
    path('auth/password/forgot/', forgot_password, name='password-forgot'),
    path('auth/password/reset/confirm/', reset_password_confirm, name='password-reset-confirm'),
    
    path('auth/google/', google_sign_in, name='google-sign-in'),
    path('auth/google/registration/', google_complete_registration, name='google-registration'),

    path('api/guarani/plan-carrera/', PlanCarreraView.as_view(), name='guarani-plan-carrera'),
    path('api/guarani/oferta-comisiones/', OfertaComisionesView.as_view(), name='guarani-oferta-comisiones'),

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),name='schema-swagger-ui')
]

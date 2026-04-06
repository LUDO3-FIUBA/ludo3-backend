from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html

from .forms import StaffCreateForm
from .models import *
from .services.notification_service import NotificationService
from .services.siu_service import SiuService
from .utils import memoized


@memoized
def departments():
    return SiuService().list_departments()

class AuditLogAdmin(admin.ModelAdmin):

    search_fields = ['user__first_name', 'user__last_name', 'user__dni', 'related_user__first_name', 'related_user__last_name', 'related_user__dni', 'log']

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(AuditLog, AuditLogAdmin)
admin.site.register(Commission)
@memoized
def subjects():
    return SiuService().list_subjects()


class StaffUser(User):
    class Meta:
        verbose_name = "Usuario Administrador"
        verbose_name_plural = "Usuarios Administradores"
        proxy = True


class StaffInline(admin.TabularInline):
    model = Staff
    fieldsets = [
        (None, {
            'fields': ('department_siu_id',)
            }),
        ]


@admin.register(StaffUser)
class StaffUserAdmin(UserAdmin):
    inlines = [StaffInline]

    exclude = ('user_permissions', 'is_student', 'is_teacher', 'date_joined', 'username', 'last_login', 'active', 'password', 'updated_at', 'is_staff', 'is_superuser')
    can_delete = False
    list_display = ('dni', 'first_name', 'last_name', 'department_siu_id')
    search_fields = ('dni', 'first_name', 'last_name', 'department_siu_id')
    ordering = ('dni', 'first_name', 'last_name')

    add_form = StaffCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'dni', 'first_name', 'last_name', 'password1', 'password2', 'groups')}
        ),
    )

    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'dni', 'first_name', 'last_name', 'groups')}
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)

    def department_siu_id(self, obj):
        return obj.staff.department_siu_id

    department_siu_id.short_description = "SIU ID del Departamento"


class StudentCommonAdmin(admin.ModelAdmin):
    inline_type = 'tabular'
    inline_reverse = [('user', {'fields': ['first_name', 'last_name', 'dni']})]

    list_display = ('dni', 'first_name', 'last_name', 'padron')
    exclude = ("face_encodings", 'inscripto', 'user')
    search_fields = ('dni', 'first_name', 'last_name', 'padron')
    readonly_fields = ('dni', 'first_name', 'last_name', 'padron')
    ordering = ('padron',)

    def get_password(self, obj):
        return obj.user.password

    def dni(self, obj):
        return obj.user.dni
    dni.short_description = "DNI"

    def first_name(self, obj):
        return obj.user.first_name
    first_name.short_description = "Nombre"

    def last_name(self, obj):
        return obj.user.last_name
    last_name.short_description = "Apellido"

    def get_last_login(self, obj):
        return obj.user.last_login

    def get_date_joined(self, obj):
        return obj.user.date_joined


@admin.register(Student)
class StudentRegularAdmin(StudentCommonAdmin):
    title = "Regular Student"

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super().get_queryset(request)
        return qs.filter(inscripto=True)


class PreRegisteredStudent(Student):
    class Meta:
        verbose_name = "Estudiante pre registrado"
        verbose_name_plural = "Estudiantes pre registrados"
        proxy = True


@admin.register(PreRegisteredStudent)
class StudentPreRegistered(StudentCommonAdmin):
    title = "Student to Register"

    list_display = ('dni', 'revisar_boton')
    readonly_fields = ('dni', 'revisar_boton')

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super().get_queryset(request)
        return qs.filter(inscripto=False)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(?P<student_id>.+)/revisar/$',
                self.admin_site.admin_view(self.revisar),
                name='revisar'),
            url(r'^(?P<student_id>.+)/aprobar/$',
                self.admin_site.admin_view(self.aprobar),
                name='aprobar'),
            url(r'^(?P<student_id>.+)/rechazar/$',
                self.admin_site.admin_view(self.rechazar),
                name='rechazar'),
        ]
        return my_urls + urls

    def revisar_boton(self, obj):
        return format_html(
            '<a class="button" href="{}">Revisar</a>',
            reverse('admin:revisar', args=[obj.pk]),
        )

    actions = ['revisar', 'aprobar', 'rechazar']


    def revisar(self, request, student_id):
        student = self.get_object(request, student_id)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['student'] = student
        context['title'] = "Revisar"

        return TemplateResponse(
            request,
            'admin/register_student.html',
            context
        )

    def aprobar(self, request, student_id):
        student = self.get_object(request, student_id)
        student.inscripto = True
        student.save()
        self.message_user(request, f"El estudiante {student.user.email} ha sido registrado")
        url = reverse(
            'admin:backend_preregisteredstudent_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    def rechazar(self, request, student_id):
        student = self.get_object(request, student_id)
        email = student.user.email
        student.user.delete()
        self.message_user(request, f"El estudiante {email} ha sido reseteado")
        url = reverse(
            'admin:backend_preregisteredstudent_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)

    revisar.short_description = "Revisar Alumno"


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    inline_type = 'tabular'
    inline_reverse = [('user', {'fields': ['first_name', 'last_name', 'dni']})]

    list_display = ('dni', 'first_name', 'last_name', 'siu_id', 'legajo')
    exclude = ("face_encodings", 'user')
    search_fields = ('dni', 'first_name', 'last_name', 'siu_id', 'legajo')
    readonly_fields = ('dni', 'first_name', 'last_name', 'siu_id', 'legajo')
    ordering = ('legajo',)

    def get_password(self, obj):
        return obj.user.password

    def dni(self, obj):
        return obj.user.dni
    dni.short_description = "DNI"

    def first_name(self, obj):
        return obj.user.first_name
    first_name.short_description = "Nombre"

    def last_name(self, obj):
        return obj.user.last_name
    last_name.short_description = "Apellido"

    def get_last_login(self, obj):
        return obj.user.last_login

    def get_date_joined(self, obj):
        return obj.user.date_joined


@admin.register(FinalExam)
class FinalExamAdmin(admin.ModelAdmin):
    title = "FinalExam"

    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('final', 'student', 'grade'),
        }),
    )

    list_display = ('subject', 'student', 'date', 'grade')
    search_fields = ('student', 'grade')
    ordering = ('student', 'grade')
    readonly_fields = ('final', 'student', 'grade')

    def date(self, obj):
        return obj.final.date
    date.short_description = "Fecha"

    def subject(self, obj):
        return obj.final.subject()['name']
    subject.short_description = "Materia"


class FinalToApprove(Final):
    class Meta:
        verbose_name = "Fecha para aprobar"
        verbose_name_plural = "Fechas para aprobar"
        proxy = True


@admin.register(FinalToApprove)
class FinalToApproveAdmin(admin.ModelAdmin):
    title = "Final Date to Approve"
    fields = ('subject_name', 'teacher', 'date')
    exclude = ('updated_at',)
    readonly_fields = ('subject_name', 'department', 'teacher', 'date')
    list_display = ('subject_name', 'department', 'teacher', 'date', 'approve', 'reject')
    ordering = ('subject_name', 'teacher', 'date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser and request.user.staff.department_siu_id:
            owning_subjects = SiuService().list_subjects({"departamentoId": request.user.staff.department_siu_id})
            qs = qs.filter(subject_siu_id__in=[s["id"] for s in owning_subjects])
        return qs.filter(status=Final.Status.DRAFT)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(?P<final_id>.+)/approve/$',
                self.admin_site.admin_view(self.approve_action),
                name='approve_action'),
            url(r'^(?P<final_id>.+)/reject/$',
                self.admin_site.admin_view(self.reject_action),
                name='reject_action'),
        ]
        return my_urls + urls

    def department(self, obj):
        for subject in subjects():
            if subject['id'] == obj.subject_siu_id:
                for department in departments():
                    if department['id'] == subject['department_id']:
                        return department['name']
    department.short_description = "Departamento"

    def approve(self, obj):
        return format_html(
            '<a class="button" href="{}">Aprobar</a>',
            reverse('admin:approve_action', args=[obj.pk]),
        )
    approve.short_description = "Aprobar"

    def reject(self, obj):
        return format_html(
            '<a class="button" href="{}">Rechazar</a>',
            reverse('admin:reject_action', args=[obj.pk]),
        )
    reject.short_description = "Rechazar"

    actions = ['approve_action', 'reject_action']

    def approve_action(self, request, final_id):
        final = self.get_object(request, final_id)

        siu_final = SiuService().create_final(final.teacher.siu_id, final.subject_siu_id,
                                              int(final.date.timestamp()))

        final.siu_id = siu_final["id"]
        final.status = Final.Status.OPEN
        final.save()

        NotificationService().notify_date_approved(final)

        self.message_user(request, "Final date approved")
        url = reverse(
            'admin:backend_finaltoapprove_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)
    approve_action.short_description = "Aprobar Fechas"

    def reject_action(self, request, final_id):
        final = self.get_object(request, final_id)
        final.status = Final.Status.REJECTED
        final.save()

        self.message_user(request, f"Final date rejected", level=messages.WARNING)
        url = reverse(
            'admin:backend_finaltoapprove_changelist',
            current_app=self.admin_site.name,
        )
        return HttpResponseRedirect(url)
    reject_action.short_description = "Rechazar Fechas"


@admin.register(Final)
class FinalAdmin(admin.ModelAdmin):
    title = "Final"
    fields = ('subject_name', 'teacher', 'date', 'qrid')
    exclude = ('updated_at',)
    readonly_fields = ('subject_name', 'subject_siu_id', 'qrid')
    ordering = ('subject_name', 'teacher', 'date')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            owning_subjects = SiuService().list_subjects({"departamentoId": request.user.staff.department_siu_id})
            qs = qs.filter(subject_siu_id__in=[s["id"] for s in owning_subjects])
        return qs.filter(status__in=(Final.Status.OPEN, Final.Status.PENDING_ACT, Final.Status.ACT_SENT))

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(?P<final_id>.+)/download/$',
                self.admin_site.admin_view(self.download_action),
                name='download_action')
        ]
        return my_urls + urls

    list_display = ('subject_name', 'department', 'teacher', 'date', 'download_qr')
    search_fields = ('subject_name', 'date',)

    def department(self, obj):
        for subject in subjects():
            if subject['id'] == obj.subject_siu_id:
                for department in departments():
                    if department['id'] == subject['department_id']:
                        return department['name']
    department.short_description = "Departamento"

    def download_qr(self, obj):
        return format_html(
            '<a class="button" href="{}">Descargar QR</a>',
            reverse('admin:download_action', args=[obj.pk]),
        )
    download_qr.short_description="Descargar QR"

    actions = ['download_action']

    def download_action(self, request, final_id):
        import io

        import qrcode

        final = self.get_object(request, final_id)

        qr = qrcode.make(final.qrid)

        output = io.BytesIO()
        qr.save(output, format='PNG')
        file = output.getvalue()

        file_response = HttpResponse(file, content_type='image/png')
        file_response['Content-Disposition'] = f"attachment; filename={final.teacher.user.last_name}-{final.date.strftime('%Y-%m-%d_%H_%M')}.png"
        return file_response
    download_action.short_description="Descargar QR"


class SemesterScheduleInline(admin.TabularInline):
    model = SemesterSchedule
    extra = 1
    fields = ('day_of_week', 'start_time', 'end_time')


class SemesterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'commission', 'start_date', 'year_moment')
    search_fields = ('commission__subject_name',)
    inlines = [SemesterScheduleInline]


admin.site.register(Semester, SemesterAdmin)


@admin.register(AcademicCalendarEvent)
class AcademicCalendarEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'year', 'start_date', 'end_date')
    list_filter = ('category', 'year')
    search_fields = ('name',)
    ordering = ('year', 'start_date')

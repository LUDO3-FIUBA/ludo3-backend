from datetime import timedelta, timezone

import factory
from faker import Faker

from backend.models import Final
from backend.models.catalog import Catalog, CatalogItem
from backend.models.commission import Commission
from backend.models.department import Department
from backend.models.form import Form, FormField, FormFieldOption
from backend.models.form_ownership import FormOwnershipGroup, FormOwnershipMember
from backend.models.form_submission import FormSubmission
from backend.models.form_types import FormFieldType, FormType
from backend.models.secretary import Secretary
from backend.models.semester import Semester
from backend.models.staff import Staff
from backend.models.user import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.User"

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    dni = factory.Faker("numerify", text="########")
    email = factory.Faker("ascii_safe_email")
    password = factory.Faker("password", length=10)


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Student"

    padron = factory.Faker("numerify", text="######")
    face_encodings = []
    user = factory.SubFactory(UserFactory, is_student=True)


class TeacherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Teacher"

    legajo = factory.Faker("numerify", text="######")
    siu_id = factory.Faker("numerify", text="###")
    face_encodings = []
    user = factory.SubFactory(UserFactory, is_teacher=True)


class FinalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Final"

    date = factory.Faker("date_time", tzinfo=timezone.utc)
    siu_id = factory.Faker("numerify", text="###")
    subject_name = Faker().word()
    subject_siu_id = factory.Faker("numerify", text="###")
    qrid = Faker().uuid4()
    status = Faker().random_choices(elements=Final.Status, length=1)[0]
    teacher = factory.SubFactory(TeacherFactory)


class FinalExamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.FinalExam"

    grade = factory.Faker("random_int", min=0, max=10)
    student = factory.SubFactory(StudentFactory)
    final = factory.SubFactory(FinalFactory)


class CommissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Commission"

    chief_teacher = factory.SubFactory(TeacherFactory)
    subject_siu_id = factory.Faker("numerify", text="###")
    subject_name = factory.Faker("word")
    siu_id = factory.Faker("numerify", text="###")


class SemesterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Semester"

    commission = factory.SubFactory(CommissionFactory)
    year_moment = factory.Iterator(
        [
            Semester.YearMoment.FIRST_SEMESTER,
            Semester.YearMoment.SECOND_SEMESTER,
            Semester.YearMoment.INTENSIVE_WINTER,
            Semester.YearMoment.INTENSIVE_SUMMER,
        ]
    )
    start_date = factory.Faker("date_time", tzinfo=timezone.utc)


class EvaluationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Evaluation"

    semester = factory.SubFactory(SemesterFactory)
    evaluation_name = factory.Faker("sentence")
    is_graded = factory.Faker("boolean")
    is_gradeable = True
    passing_grade = factory.Faker("random_int", min=0, max=10)
    start_date = factory.Faker("date_time", tzinfo=timezone.utc)
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timedelta(days=1))


class SubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.EvaluationSubmission"

    evaluation = factory.SubFactory(EvaluationFactory)
    student = factory.SubFactory(StudentFactory)
    submission_status = None  # Default to None or another default value
    grade = None  # Default to None or another default value
    grader = None  # Default to None or another default value
    created_at = factory.Faker("date_time", tzinfo=timezone.utc)
    updated_at = factory.Faker("date_time", tzinfo=timezone.utc)


class TeacherRoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.TeacherRole"

    commission = factory.SubFactory(CommissionFactory)
    teacher = factory.SubFactory(TeacherFactory)
    grader_weight = factory.Faker("random_int", min=1, max=10)
    role = factory.Iterator(
        ["T", "A", "C"]
    )  # Assuming 'T' for Teacher, 'A' for Assistant, 'C' for Collaborator


class AdminUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    dni = factory.Faker("numerify", text="########")
    email = factory.Faker("ascii_safe_email")
    password = factory.Faker("password", length=10)
    is_staff = True
    is_superuser = True
    is_student = False
    is_teacher = False


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Faker("company")
    location = factory.Faker("address")
    schedule = ""
    contact_info = ""
    procedures = ""


class SecretaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Secretary

    name = factory.Faker("company")
    parent_secretary = None
    location = factory.Faker("address")
    schedule = ""
    contact_info = ""


class DeptStaffUserFactory(factory.django.DjangoModelFactory):
    """Creates a non-super staff user associated with a Department."""
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    dni = factory.Faker("numerify", text="########")
    email = factory.Faker("ascii_safe_email")
    password = factory.Faker("password", length=10)
    is_staff = True
    is_superuser = False
    is_student = False
    is_teacher = False


class DeptStaffFactory(factory.django.DjangoModelFactory):
    """Creates a Staff record linked to a Department (non-super admin)."""
    class Meta:
        model = Staff

    user = factory.SubFactory(DeptStaffUserFactory)
    department = factory.SubFactory(DepartmentFactory)
    department_siu_id = 0


class SecretaryStaffFactory(factory.django.DjangoModelFactory):
    """Creates a Staff record linked to a Secretary (non-super admin)."""
    class Meta:
        model = Staff

    user = factory.SubFactory(DeptStaffUserFactory)
    secretary = factory.SubFactory(SecretaryFactory)
    department_siu_id = 0


class FormOwnershipGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormOwnershipGroup

    name = factory.Sequence(lambda n: f"Grupo {n}")


class FormOwnershipMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormOwnershipMember

    group = factory.SubFactory(FormOwnershipGroupFactory)
    entity_type = FormOwnershipMember.DEPARTMENT
    entity_id = factory.Sequence(lambda n: n + 1)
    is_editor = False


class FormTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormType

    form_type_value = factory.Iterator(['Digital', 'Documento'])


class FormFieldTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormFieldType

    form_field_type_value = factory.Iterator(['texto', 'numero', 'padron', 'mail', 'options', 'catalog', 'checkbox', 'adjunto'])


class CatalogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Catalog

    catalog_key = factory.Sequence(lambda n: f"catalog_{n}")
    catalog_name = factory.Faker("word")
    catalog_description = None


class CatalogItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CatalogItem

    catalog = factory.SubFactory(CatalogFactory)
    catalog_item_value = factory.Sequence(lambda n: str(n))
    catalog_item_label = factory.Faker("word")
    catalog_item_order = factory.Sequence(lambda n: n)
    catalog_item_active = True


class FormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Form

    form_name = factory.Faker("sentence", nb_words=3)
    form_description = factory.Faker("sentence")
    form_information = None
    ownership_group = factory.SubFactory(FormOwnershipGroupFactory)
    form_type = factory.SubFactory(FormTypeFactory)


class FormFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormField

    form = factory.SubFactory(FormFactory)
    form_field_label = factory.Faker("word")
    form_field_type = factory.SubFactory(FormFieldTypeFactory)
    form_field_require = False
    form_field_order = factory.Sequence(lambda n: n)
    catalog = None


class FormFieldOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormFieldOption

    form_field = factory.SubFactory(FormFieldFactory)
    form_option_value = factory.Sequence(lambda n: str(n))
    form_option_label = factory.Faker("word")


class FormSubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FormSubmission

    form = factory.SubFactory(FormFactory)
    user = factory.SubFactory(UserFactory, is_student=True)
class AttendanceQRCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.AttendanceQRCode"

    semester = factory.SubFactory(SemesterFactory)
    owner_teacher = factory.SubFactory(TeacherFactory)
    created_at = factory.Faker("date_time", tzinfo=timezone.utc)
    expires_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(hours=3))
    qrid = factory.Faker("uuid4")


class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.Attendance"

    semester = factory.SubFactory(SemesterFactory)
    student = factory.SubFactory(StudentFactory)
    qr_code = factory.SubFactory(AttendanceQRCodeFactory)
    submitted_at = factory.Faker("date_time", tzinfo=timezone.utc)

from datetime import timezone

import factory
from faker import Faker

from backend.models import Final
from backend.models.commission import Commission
from backend.models.semester import Semester


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
    passing_grade = factory.Faker("random_int", min=0, max=10)
    start_date = factory.Faker("date_time", tzinfo=timezone.utc)
    end_date = factory.Faker("date_time", tzinfo=timezone.utc)


class SubmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "backend.EvaluationSubmission"

    evaluation = factory.SubFactory(EvaluationFactory)
    student = factory.SubFactory(StudentFactory)
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

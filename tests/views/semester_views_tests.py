from datetime import timedelta, timezone

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Semester, CommissionInscription
from tests.factories import (
    CommissionFactory,
    EvaluationFactory,
    SemesterFactory,
    SubmissionFactory,
    TeacherFactory,
    TeacherRoleFactory,
    StudentFactory,
    AttendanceQRCodeFactory,
    AttendanceFactory,
)


class SemesterCommissionPresentSemesterTests(APITestCase):
    def setUp(self) -> None:
        """Setup test data for semester commission tests."""
        self.teacher = TeacherFactory()
        self.other_teacher = TeacherFactory()

        self.commission = CommissionFactory(chief_teacher=self.teacher)

        current_year = timezone.now().year
        self.semester = SemesterFactory(
            commission=self.commission,
            year_moment=Semester.YearMoment.FIRST_SEMESTER,
            start_date=timezone.now(),
        )

        self.students = StudentFactory.create_batch(3)
        for student in self.students:
            CommissionInscription.objects.create(
                semester=self.semester,
                student=student,
                status='P'
            )

        self.evaluation1 = EvaluationFactory(
            semester=self.semester,
            is_gradeable=True,
            passing_grade=5
        )
        self.evaluation2 = EvaluationFactory(
            semester=self.semester,
            is_gradeable=False,
        )

        self.submission1 = SubmissionFactory(
            evaluation=self.evaluation1,
            student=self.students[0],
            grade=7,
        )
        self.submission2 = SubmissionFactory(
            evaluation=self.evaluation1,
            student=self.students[1],
            grade=None,
        )
        self.submission3 = SubmissionFactory(
            evaluation=self.evaluation2,
            student=self.students[2],
            submission_status='APROBADO',
            grade=None,
        )

        self.qr_code = AttendanceQRCodeFactory(
            semester=self.semester,
            owner_teacher=self.teacher
        )

        AttendanceFactory(semester=self.semester, student=self.students[0], qr_code=self.qr_code)
        AttendanceFactory(semester=self.semester, student=self.students[1], qr_code=self.qr_code)

        self.commission_present_semester_uri = "/api/semesters/commission_present_semester/"

    def test_commission_present_semester_success(self):
        """Test that a teacher can get semester stats for their commission."""
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(
            self.commission_present_semester_uri,
            {"commission_id": self.commission.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data["id"], self.semester.id)
        self.assertEqual(response.data["year_moment"], Semester.YearMoment.FIRST_SEMESTER)

        self.assertEqual(response.data["attendance_qrs_count"], 1)

        self.assertEqual(len(response.data["students"]), 3)

        student_0 = next(s for s in response.data["students"] if s["padron"] == self.students[0].padron)
        self.assertEqual(student_0["attendances_count"], 1)
        self.assertEqual(len(student_0["submissions"]), 1)
        self.assertEqual(student_0["submissions"][0]["evaluation_id"], self.evaluation1.id)
        self.assertEqual(student_0["submissions"][0]["grade"], 7)
        self.assertIsNone(student_0["submissions"][0]["submission_status"])

        student_1 = next(s for s in response.data["students"] if s["padron"] == self.students[1].padron)
        self.assertEqual(student_1["attendances_count"], 1)
        self.assertEqual(len(student_1["submissions"]), 1)
        self.assertEqual(student_1["submissions"][0]["grade"], None)

        student_2 = next(s for s in response.data["students"] if s["padron"] == self.students[2].padron)
        self.assertEqual(student_2["attendances_count"], 0)
        self.assertEqual(len(student_2["submissions"]), 1)
        self.assertEqual(student_2["submissions"][0]["submission_status"], "APROBADO")
        self.assertIsNone(student_2["submissions"][0]["grade"])

    def test_commission_present_semester_teacher_not_in_commission(self):
        """Test that a teacher not in the commission gets 403."""
        self.client.force_authenticate(user=self.other_teacher.user)
        response = self.client.get(
            self.commission_present_semester_uri,
            {"commission_id": self.commission.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Teacher not a member", response.data)

    def test_commission_present_semester_missing_commission_id(self):
        """Test that missing commission_id returns 400."""
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(
            self.commission_present_semester_uri,
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_commission_present_semester_invalid_commission_id(self):
        """Test that invalid commission_id returns 400."""
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(
            self.commission_present_semester_uri,
            {"commission_id": "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_commission_present_semester_not_found(self):
        """Test that a non-existent semester returns 404."""
        other_commission = CommissionFactory(chief_teacher=self.teacher)

        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(
            self.commission_present_semester_uri,
            {"commission_id": other_commission.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_commission_present_semester_unauthenticated(self):
        """Test that unauthenticated request returns 401."""
        response = self.client.get(
            self.commission_present_semester_uri,
            {"commission_id": self.commission.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_commission_present_semester_payload_structure(self):
        """Test that the response payload has the correct structure."""
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(
            self.commission_present_semester_uri,
            {"commission_id": self.commission.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        required_fields = [
            "id",
            "year_moment",
            "start_date",
            "commission",
            "evaluations",
            "students",
            "classes_amount",
            "minimum_attendance",
            "schedules",
            "attendance_qrs_count",
        ]
        for field in required_fields:
            self.assertIn(field, response.data)

        for student in response.data["students"]:
            required_student_fields = [
                "id",
                "first_name",
                "last_name",
                "dni",
                "email",
                "padron",
                "attendances_count",
                "submissions",
            ]
            for field in required_student_fields:
                self.assertIn(field, student)

        for student in response.data["students"]:
            for submission in student["submissions"]:
                required_submission_fields = [
                    "evaluation_id",
                    "grade",
                    "submission_status",
                ]
                for field in required_submission_fields:
                    self.assertIn(field, submission)

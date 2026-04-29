from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Attendance, AttendanceQRCode
from tests.factories import SemesterFactory, StudentFactory, TeacherFactory


class AttendanceStudentViewsTests(APITestCase):
    def setUp(self) -> None:
        self.student = StudentFactory()
        self.other_student = StudentFactory()
        self.teacher = TeacherFactory()

        self.semester = SemesterFactory()
        self.semester.students.add(self.student, self.other_student)

        self.other_semester = SemesterFactory()
        self.other_semester.students.add(self.student)

        self.my_attendances_url = "/api/semesters/attendance/my_attendances/"

    def test_my_attendances_returns_status_for_all_semester_classes(self):
        qr_1 = AttendanceQRCode.objects.create(semester=self.semester, owner_teacher=self.teacher)
        qr_2 = AttendanceQRCode.objects.create(semester=self.semester, owner_teacher=self.teacher)
        qr_3 = AttendanceQRCode.objects.create(semester=self.semester, owner_teacher=self.teacher)
        qr_other_semester = AttendanceQRCode.objects.create(
            semester=self.other_semester,
            owner_teacher=self.teacher,
        )

        own_attendance_1 = Attendance.objects.create(
            semester=self.semester,
            student=self.student,
            qr_code=qr_1,
        )
        own_attendance_2 = Attendance.objects.create(
            semester=self.semester,
            student=self.student,
            qr_code=qr_2,
        )

        Attendance.objects.create(
            semester=self.semester,
            student=self.other_student,
            qr_code=qr_1,
        )
        Attendance.objects.create(
            semester=self.other_semester,
            student=self.student,
            qr_code=qr_other_semester,
        )

        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.my_attendances_url, {"semester_id": self.semester.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        returned_qrids = {item["qrid"] for item in response.data}
        self.assertEqual(returned_qrids, {str(qr_1.qrid), str(qr_2.qrid), str(qr_3.qrid)})

        statuses_by_qrid = {item["qrid"]: item for item in response.data}

        self.assertTrue(statuses_by_qrid[str(qr_1.qrid)]["attended"])
        self.assertTrue(statuses_by_qrid[str(qr_2.qrid)]["attended"])
        self.assertFalse(statuses_by_qrid[str(qr_3.qrid)]["attended"])

        self.assertIsNotNone(statuses_by_qrid[str(qr_1.qrid)]["submitted_at"])
        self.assertIsNotNone(statuses_by_qrid[str(qr_2.qrid)]["submitted_at"])
        self.assertIsNone(statuses_by_qrid[str(qr_3.qrid)]["submitted_at"])

        for item in response.data:
            self.assertIn("created_at", item)
            self.assertIn("expires_at", item)
            self.assertIn("attended", item)
            self.assertIn("submitted_at", item)
            self.assertNotIn("semester", item)
            self.assertNotIn("student", item)

    def test_my_attendances_forbidden_when_student_not_in_commission(self):
        outsider_student = StudentFactory()

        self.client.force_authenticate(user=outsider_student.user)
        response = self.client.get(self.my_attendances_url, {"semester_id": self.semester.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, "Student not in commission")

    def test_my_attendances_unauthenticated(self):
        response = self.client.get(self.my_attendances_url, {"semester_id": self.semester.id})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_my_attendances_forbidden_for_teacher(self):
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(self.my_attendances_url, {"semester_id": self.semester.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
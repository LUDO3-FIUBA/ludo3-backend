from datetime import timezone, timedelta

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

    # --- QR mode attendance submission ---

    def test_qr_mode_creates_attendance_without_location(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/api/semesters/attendance/", {"qrid": str(qr.qrid)})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["location_valid"])
        attendance = Attendance.objects.get(student=self.student, qr_code=qr)
        self.assertIsNone(attendance.location_valid)

    def test_qr_mode_duplicate_scan_is_rejected(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        self.client.post("/api/semesters/attendance/", {"qrid": str(qr.qrid)})
        response = self.client.post("/api/semesters/attendance/", {"qrid": str(qr.qrid)})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_qr_mode_expired_qr_is_rejected(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr',
            expires_at=tz.now() - timedelta(minutes=1),
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/api/semesters/attendance/", {"qrid": str(qr.qrid)})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- QR + location mode attendance submission ---

    def test_qr_location_within_campus_records_valid_attendance(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.58881221211288,
            "longitude": -58.39658985864721,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["location_valid"])
        attendance = Attendance.objects.get(student=self.student, qr_code=qr)
        self.assertTrue(attendance.location_valid)

    def test_qr_location_outside_campus_returns_422_no_record_created(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.6100,
            "longitude": -58.4200,
        })

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertFalse(Attendance.objects.filter(student=self.student, qr_code=qr).exists())

    def test_qr_location_outside_campus_allows_retry_inside(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        first = self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.6100,
            "longitude": -58.4200,
        })
        self.assertEqual(first.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        second = self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.58881221211288,
            "longitude": -58.39658985864721,
        })
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertTrue(second.data["location_valid"])
        self.assertEqual(Attendance.objects.filter(student=self.student, qr_code=qr).count(), 1)

    def test_qr_location_missing_coords_returns_400(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/api/semesters/attendance/", {"qrid": str(qr.qrid)})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_qr_location_duplicate_rejected(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() + timedelta(hours=3),
        )
        self.client.force_authenticate(user=self.student.user)
        self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.58881221211288,
            "longitude": -58.39658985864721,
        })
        response = self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.58881221211288,
            "longitude": -58.39658985864721,
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_qr_location_expired_qr_is_rejected(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() - timedelta(minutes=1),
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.post("/api/semesters/attendance/", {
            "qrid": str(qr.qrid),
            "latitude": -34.58881221211288,
            "longitude": -58.39658985864721,
        })

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_attendances_includes_location_valid_for_qr_location_session(self):
        from django.utils import timezone as tz
        qr = AttendanceQRCode.objects.create(
            semester=self.semester,
            owner_teacher=self.teacher,
            mode='qr_location',
            campus='las_heras',
            expires_at=tz.now() + timedelta(hours=3),
        )
        Attendance.objects.create(
            semester=self.semester,
            student=self.student,
            qr_code=qr,
            latitude=-34.58881221211288,
            longitude=-58.39658985864721,
            location_valid=True,
        )
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.my_attendances_url, {"semester_id": self.semester.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session_data = next(item for item in response.data if item["qrid"] == str(qr.qrid))
        self.assertIn("location_valid", session_data)
        self.assertTrue(session_data["location_valid"])
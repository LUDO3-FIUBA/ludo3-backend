from datetime import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import CommissionInscription
from backend.views.utils import get_current_semester, get_current_year
from ..factories import (CommissionFactory, SemesterFactory, StudentFactory,
                         TeacherFactory)


class TeacherProfileViewsTests(APITestCase):
    def setUp(self):
        self.teacher = TeacherFactory()
        self.teacher.user.linkedin_url = 'https://linkedin.com/in/teacher'
        self.teacher.user.github_url = 'https://github.com/teacher'
        self.teacher.user.save()

        self.student = StudentFactory()
        self.url = f"/api/teachers/{self.teacher.user_id}/profile/"

    def _active_semester(self, commission):
        return SemesterFactory(
            commission=commission,
            year_moment=get_current_semester(),
            start_date=datetime(get_current_year(), 1, 1),
        )

    def test_unauthenticated_gets_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_teacher_can_view_own_profile(self):
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['linkedin_url'], 'https://linkedin.com/in/teacher')
        self.assertEqual(response.data['github_url'], 'https://github.com/teacher')

    def test_other_teacher_cannot_view_profile(self):
        other = TeacherFactory()
        self.client.force_authenticate(user=other.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_with_active_inscription_as_chief_can_view(self):
        commission = CommissionFactory(chief_teacher=self.teacher)
        semester = self._active_semester(commission)
        CommissionInscription.objects.create(student=self.student, semester=semester, status='A')

        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['linkedin_url'], 'https://linkedin.com/in/teacher')

    def test_student_without_inscription_gets_404(self):
        commission = CommissionFactory(chief_teacher=self.teacher)
        self._active_semester(commission)
        # no inscription created

        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_with_pending_inscription_gets_404(self):
        commission = CommissionFactory(chief_teacher=self.teacher)
        semester = self._active_semester(commission)
        CommissionInscription.objects.create(student=self.student, semester=semester, status='P')

        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_with_inscription_outside_active_semester_gets_404(self):
        commission = CommissionFactory(chief_teacher=self.teacher)
        old_semester = SemesterFactory(
            commission=commission,
            year_moment=get_current_semester(),
            start_date=datetime(get_current_year() - 2, 1, 1),
        )
        CommissionInscription.objects.create(student=self.student, semester=old_semester, status='A')

        self.client.force_authenticate(user=self.student.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_teacher_returns_404(self):
        self.client.force_authenticate(user=self.student.user)
        response = self.client.get("/api/teachers/999999/profile/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

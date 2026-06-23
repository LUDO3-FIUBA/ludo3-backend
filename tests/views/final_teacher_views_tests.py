from datetime import datetime
from unittest import mock

from faker import Faker
from rest_framework import status, serializers
from rest_framework.test import APITestCase

from backend.client.siu_client import SiuClient
from backend.models import Final
from backend.services.image_validator_service import ImageValidatorService
from backend.services.notification_service import NotificationService
from backend.views.utils import get_current_semester, get_current_year
from ..factories import (CommissionFactory, FinalExamFactory, FinalFactory,
                         SemesterFactory, TeacherFactory)


class FinalTeacherViewsTests(APITestCase):
    def setUp(self) -> None:
        self.teacher = TeacherFactory()
        self.subject_siu_id = Faker().numerify(text='###')
        self.subject_name = Faker().word()

    def _active_commission(self, chief_teacher=None, subject_siu_id=None):
        commission = CommissionFactory(
            chief_teacher=chief_teacher or self.teacher,
            subject_siu_id=subject_siu_id or self.subject_siu_id,
        )
        SemesterFactory(
            commission=commission,
            year_moment=get_current_semester(),
            start_date=datetime(get_current_year(), 1, 1),
        )
        return commission

    def test_list_success(self):
        """
        Should fetch all finals belonging to authenticated teacher and which have the subject_siu_id
        passed by parameter
        """
        list_url = f"/api/finals/"
        self.client.force_authenticate(user=self.teacher.user)

        finals = FinalFactory.create_batch(size=3, teacher=self.teacher, subject_siu_id=self.subject_siu_id)
        FinalFactory.create_batch(size=3, teacher=self.teacher, subject_siu_id=self.subject_siu_id + "2")

        mock_subject = [{
            "id": 1,
            "codigo": "62.01",
            "nombre": "Física I",
            "correlativas": []
        }]

        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            response = self.client.get(list_url, {"subject_siu_id": self.subject_siu_id}, format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), len(finals))
            self.assertEqual(
                sorted([final['id'] for final in response.data]),
                sorted([final.id for final in finals])
            )

    def test_list_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        list_url = f"/api/finals/"
        response = self.client.get(list_url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_success(self):
        """
        Should fetch a final with all its final exams an students data
        """
        self.client.force_authenticate(user=self.teacher.user)

        final = FinalFactory(teacher=self.teacher)
        final_exams = FinalExamFactory.create_batch(size=3, final=final, grade=None)

        url = f"/api/finals/{final.id}/"

        mock_subject = {
            "id": 2,
            "codigo": "62.02",
            "nombre": "Física II",
            "correlativas": ["62.01"]
        }

        mock_correlatives = [{
            "id": 1,
            "codigo": "62.01",
            "nombre": "Física I",
            "correlativas": []
        }]

        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            with mock.patch.object(SiuClient, "list_subjects", return_value=mock_correlatives):
                response = self.client.get(url, format='json')

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['id'], final.pk)
                self.assertEqual(response.data['date'], serializers.DateTimeField().to_representation(final.date))
                self.assertEqual(len(response.data['final_exams']), len(final_exams))

    def test_detail_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        url = f"/api/finals/1/"
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_success(self):
        """
        Should create a final shared with the given commissions
        """

        self.client.force_authenticate(user=self.teacher.user)
        commission_a = self._active_commission()
        commission_b = self._active_commission()
        final_fields = {
            'subject_name': self.subject_name,
            'subject_siu_id': self.subject_siu_id,
            'timestamp': Faker().unix_time(),
            'commission_ids': [commission_a.id, commission_b.id],
        }
        url = f"/api/finals/"

        mock_subject = [{
            "id": 1,
            "codigo": "62.01",
            "nombre": "Física I",
            "correlativas": []
        }]

        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            response = self.client.post(url, data=final_fields, format='json')

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['date'], serializers.DateTimeField().to_representation(datetime.utcfromtimestamp(final_fields['timestamp'])))
            self.assertEqual(response.data['status'], Final.Status.DRAFT)
            self.assertEqual(
                sorted(c['id'] for c in response.data['commissions']),
                sorted([commission_a.id, commission_b.id]),
            )
            final = Final.objects.get(id=response.data['id'])
            self.assertEqual(
                sorted(final.commissions.values_list('id', flat=True)),
                sorted([commission_a.id, commission_b.id]),
            )

    def test_create_requires_at_least_one_commission(self):
        self.client.force_authenticate(user=self.teacher.user)
        response = self.client.post(
            "/api/finals/",
            data={
                'subject_name': self.subject_name,
                'subject_siu_id': self.subject_siu_id,
                'timestamp': Faker().unix_time(),
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_when_not_chief_of_any_commission(self):
        """Si no sos chief de ninguna de las commissions elegidas, se rechaza."""
        self.client.force_authenticate(user=self.teacher.user)
        other_chief = TeacherFactory()
        commission = self._active_commission(chief_teacher=other_chief)

        response = self.client.post(
            "/api/finals/",
            data={
                'subject_name': self.subject_name,
                'subject_siu_id': self.subject_siu_id,
                'timestamp': Faker().unix_time(),
                'commission_ids': [commission.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_allows_sharing_with_other_chiefs_commissions(self):
        """Si sos chief de al menos una commission elegida, podés compartir con commissions de otros chiefs."""
        self.client.force_authenticate(user=self.teacher.user)
        own = self._active_commission()
        other_chief = TeacherFactory()
        someone_elses = self._active_commission(chief_teacher=other_chief)

        response = self.client.post(
            "/api/finals/",
            data={
                'subject_name': self.subject_name,
                'subject_siu_id': self.subject_siu_id,
                'timestamp': Faker().unix_time(),
                'commission_ids': [own.id, someone_elses.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            sorted(c['id'] for c in response.data['commissions']),
            sorted([own.id, someone_elses.id]),
        )

    def test_create_rejects_mismatched_subject(self):
        self.client.force_authenticate(user=self.teacher.user)
        commission = self._active_commission(subject_siu_id=str(int(self.subject_siu_id) + 1))

        response = self.client.post(
            "/api/finals/",
            data={
                'subject_name': self.subject_name,
                'subject_siu_id': self.subject_siu_id,
                'timestamp': Faker().unix_time(),
                'commission_ids': [commission.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_commission_not_in_active_semester(self):
        self.client.force_authenticate(user=self.teacher.user)
        commission = CommissionFactory(
            chief_teacher=self.teacher,
            subject_siu_id=self.subject_siu_id,
        )
        SemesterFactory(
            commission=commission,
            year_moment=get_current_semester(),
            start_date=datetime(get_current_year() - 1, 1, 1),
        )

        response = self.client.post(
            "/api/finals/",
            data={
                'subject_name': self.subject_name,
                'subject_siu_id': self.subject_siu_id,
                'timestamp': Faker().unix_time(),
                'commission_ids': [commission.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_includes_shared_finals_for_other_chief(self):
        """Si el final compartió a una commission donde el caller es chief_teacher (no creador),
        igual debe verlo en el listado."""
        creator = TeacherFactory()
        other_chief = self.teacher

        own_commission = CommissionFactory(chief_teacher=other_chief, subject_siu_id=self.subject_siu_id)
        shared_final = FinalFactory(teacher=creator, subject_siu_id=self.subject_siu_id)
        shared_final.commissions.add(own_commission)

        self.client.force_authenticate(user=other_chief.user)
        mock_subject = [{"id": 1, "codigo": "62.01", "nombre": "x", "correlativas": []}]
        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            response = self.client.get("/api/finals/", {"subject_siu_id": self.subject_siu_id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(shared_final.id, [f['id'] for f in response.data])

    def test_list_includes_shared_finals(self):
        """
        A teacher should also see finals shared with a commission they teach in,
        even if they didn't create the final themselves.
        """
        from ..factories import TeacherRoleFactory

        chief = TeacherFactory()
        shared_commission = CommissionFactory(
            chief_teacher=chief, subject_siu_id=self.subject_siu_id,
        )
        TeacherRoleFactory(commission=shared_commission, teacher=self.teacher)

        shared_final = FinalFactory(teacher=chief, subject_siu_id=self.subject_siu_id)
        shared_final.commissions.add(shared_commission)
        own_final = FinalFactory(teacher=self.teacher, subject_siu_id=self.subject_siu_id)

        self.client.force_authenticate(user=self.teacher.user)

        mock_subject = [{
            "id": 1, "codigo": "62.01", "nombre": "Física I",
            "correlativas": [],
        }]
        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            response = self.client.get("/api/finals/", {"subject_siu_id": self.subject_siu_id}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = sorted(f['id'] for f in response.data)
        self.assertEqual(ids, sorted([shared_final.id, own_final.id]))

    def test_create_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        url = f"/api/finals/"
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_close_success(self):
        """
        Should close final, passing it's status to Pending Act
        """
        self.client.force_authenticate(user=self.teacher.user)

        final = FinalFactory(teacher=self.teacher, status=Final.Status.OPEN)

        url = f"/api/finals/{final.id}/close/"

        mock_subject = {
            "id": 1,
            "codigo": "62.01",
            "nombre": "Física I",
            "correlatives": []
        }

        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            response = self.client.post(url, format='json')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['status'], Final.Status.PENDING_ACT)


    def test_close_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        url = f"/api/finals/1/close/"
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_grade_success(self):
        """
        Should add a grade to a final
        """
        self.client.force_authenticate(user=self.teacher.user)

        final = FinalFactory(teacher=self.teacher, status=Final.Status.PENDING_ACT)
        final_exams = FinalExamFactory.create_batch(size=2, final=final, grade=None)

        grades = [{"final_exam_id": fe.id, "grade": Faker().random_int(1, 10)} for fe in final_exams]

        url = f"/api/finals/{final.id}/grade/"

        mock_subject = {
            "id": 1,
            "codigo": "62.01",
            "nombre": "Física I",
            "correlatives": []
        }

        with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):
            with mock.patch.object(SiuClient, "save_final_grades", return_value={}):
                response = self.client.put(url, format='json', data=grades)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['id'], final.id)
                for idx, fe in enumerate(response.data['final_exams']):
                    self.assertEqual(fe['grade'], grades[idx]["grade"])

    def test_grade_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        url = f"/api/finals/1/grade/"
        response = self.client.put(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_act_success(self):
        """
        Should pass the status to Act Sent
        """
        self.client.force_authenticate(user=self.teacher.user)

        final = FinalFactory(teacher=self.teacher, status=Final.Status.PENDING_ACT)

        url = f"/api/finals/{final.id}/send_act/"

        mock_subject = {
            "id": 1,
            "codigo": "62.01",
            "nombre": "Física I",
            "correlatives": []
        }

        with mock.patch.object(ImageValidatorService, "validate_identity", return_value=True):
            with mock.patch.object(SiuClient, "create_act", return_value={'id': '123AB00'}):
                with mock.patch.object(NotificationService, "notify_act", return_value=None):
                    with mock.patch.object(SiuClient, "get_subject", return_value=mock_subject):

                        response = self.client.post(url, format='json', data={'image': 'fake_image'})

                        self.assertEqual(response.status_code, status.HTTP_200_OK)
                        self.assertEqual(response.data['status'], Final.Status.ACT_SENT)
                        self.assertEqual(response.data['act'], '123AB00')

    def test_send_act_not_logged_in(self):
        """
        Should fail if unauthorized
        """
        url = f"/api/finals/1/send_act/"
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

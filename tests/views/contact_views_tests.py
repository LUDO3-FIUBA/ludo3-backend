from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Contact
from tests.factories import StudentFactory

CONTACTS_URI = '/api/contacts/'
SEARCH_URI = '/api/students/search/'


class StudentSearchViewTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory(user__first_name='Lucas', user__last_name='Salluzzi')
        self.other = StudentFactory(user__first_name='Gonzalo', user__last_name='Gordon', padron='100001')
        self.client.force_authenticate(user=self.student.user)

    def test_search_by_padron_returns_match(self):
        response = self.client.get(SEARCH_URI, {'q': self.other.padron})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        padrones = [r['padron'] for r in response.data]
        self.assertIn(self.other.padron, padrones)

    def test_search_by_name_returns_match(self):
        response = self.client.get(SEARCH_URI, {'q': 'Gonzalo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['padron'], self.other.padron)

    def test_search_excludes_self(self):
        response = self.client.get(SEARCH_URI, {'q': 'Lucas'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        padrones = [r['padron'] for r in response.data]
        self.assertNotIn(self.student.padron, padrones)

    def test_search_too_short_returns_400(self):
        response = self.client.get(SEARCH_URI, {'q': 'a'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_returns_401(self):
        self.client.logout()
        response = self.client.get(SEARCH_URI, {'q': 'Lucas'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ContactViewSetTests(APITestCase):
    def setUp(self):
        self.student = StudentFactory()
        self.other = StudentFactory()
        self.third = StudentFactory()
        self.client.force_authenticate(user=self.student.user)

    def test_send_contact_request(self):
        response = self.client.post(CONTACTS_URI, {'padron': self.other.padron})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], Contact.Status.PENDING)

    def test_cannot_add_self(self):
        response = self.client.post(CONTACTS_URI, {'padron': self.student.padron})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_request_returns_409(self):
        self.client.post(CONTACTS_URI, {'padron': self.other.padron})
        response = self.client.post(CONTACTS_URI, {'padron': self.other.padron})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_send_to_nonexistent_student_returns_404(self):
        response = self.client.post(CONTACTS_URI, {'padron': '000000'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_shows_sent_and_received(self):
        Contact.objects.create(from_student=self.student, to_student=self.other)
        Contact.objects.create(from_student=self.third, to_student=self.student)
        response = self.client.get(CONTACTS_URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_accept_contact_request(self):
        contact = Contact.objects.create(from_student=self.other, to_student=self.student)
        response = self.client.post(f'{CONTACTS_URI}{contact.pk}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact.refresh_from_db()
        self.assertEqual(contact.status, Contact.Status.ACCEPTED)

    def test_cannot_accept_own_sent_request(self):
        contact = Contact.objects.create(from_student=self.student, to_student=self.other)
        response = self.client.post(f'{CONTACTS_URI}{contact.pk}/accept/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_contact(self):
        contact = Contact.objects.create(from_student=self.student, to_student=self.other)
        response = self.client.delete(f'{CONTACTS_URI}{contact.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contact.objects.filter(pk=contact.pk).exists())

    def test_delete_received_contact(self):
        contact = Contact.objects.create(from_student=self.other, to_student=self.student)
        response = self.client.delete(f'{CONTACTS_URI}{contact.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistent_returns_404(self):
        response = self.client.delete(f'{CONTACTS_URI}9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subjects_of_accepted_contact(self):
        contact = Contact.objects.create(
            from_student=self.student, to_student=self.other, status=Contact.Status.ACCEPTED
        )
        response = self.client.get(f'{CONTACTS_URI}{contact.pk}/subjects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_subjects_of_pending_contact_returns_404(self):
        contact = Contact.objects.create(from_student=self.student, to_student=self.other)
        response = self.client.get(f'{CONTACTS_URI}{contact.pk}/subjects/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subjects_include_schedules(self):
        contact = Contact.objects.create(
            from_student=self.student, to_student=self.other, status=Contact.Status.ACCEPTED
        )
        response = self.client.get(f'{CONTACTS_URI}{contact.pk}/subjects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for subject in response.data:
            self.assertIn('schedules', subject)
            self.assertIsInstance(subject['schedules'], list)

    def test_schedule_comparison_returns_mine_and_theirs(self):
        contact = Contact.objects.create(
            from_student=self.student, to_student=self.other, status=Contact.Status.ACCEPTED
        )
        response = self.client.get(f'{CONTACTS_URI}{contact.pk}/schedule-comparison/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mine', response.data)
        self.assertIn('theirs', response.data)
        self.assertIsInstance(response.data['mine'], list)
        self.assertIsInstance(response.data['theirs'], list)

    def test_schedule_comparison_pending_contact_returns_404(self):
        contact = Contact.objects.create(from_student=self.student, to_student=self.other)
        response = self.client.get(f'{CONTACTS_URI}{contact.pk}/schedule-comparison/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        self.client.logout()
        response = self.client.get(CONTACTS_URI)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_accepted_contact_exposes_linkedin_and_github(self):
        self.other.user.linkedin_url = 'https://linkedin.com/in/other'
        self.other.user.github_url = 'https://github.com/other'
        self.other.user.save()
        Contact.objects.create(
            from_student=self.student, to_student=self.other, status=Contact.Status.ACCEPTED
        )
        response = self.client.get(CONTACTS_URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact_payload = response.data[0]['contact']
        self.assertEqual(contact_payload['linkedin_url'], 'https://linkedin.com/in/other')
        self.assertEqual(contact_payload['github_url'], 'https://github.com/other')
        self.assertIn('profile_photo', contact_payload)

    def test_pending_contact_does_not_expose_linkedin_and_github(self):
        self.other.user.linkedin_url = 'https://linkedin.com/in/other'
        self.other.user.github_url = 'https://github.com/other'
        self.other.user.save()
        Contact.objects.create(
            from_student=self.student, to_student=self.other, status=Contact.Status.PENDING
        )
        response = self.client.get(CONTACTS_URI)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact_payload = response.data[0]['contact']
        self.assertNotIn('linkedin_url', contact_payload)
        self.assertNotIn('github_url', contact_payload)

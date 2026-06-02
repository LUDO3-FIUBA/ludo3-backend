from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Contact, GroupMembership, StudyGroup
from tests.factories import StudentFactory

GROUPS_URI = '/api/study-groups/'


class StudyGroupViewSetTests(APITestCase):
    def setUp(self):
        self.creator = StudentFactory()
        self.member1 = StudentFactory()
        self.member2 = StudentFactory()
        self.client.force_authenticate(user=self.creator.user)
        # Accepted contacts so invitations work
        Contact.objects.create(from_student=self.creator, to_student=self.member1, status=Contact.Status.ACCEPTED)
        Contact.objects.create(from_student=self.creator, to_student=self.member2, status=Contact.Status.ACCEPTED)

    def test_create_group(self):
        resp = self.client.post(GROUPS_URI, {'name': 'Grupo TP Redes'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['name'], 'Grupo TP Redes')

    def test_create_group_without_name_returns_400(self):
        resp = self.client.post(GROUPS_URI, {'name': ''})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_shows_created_groups(self):
        StudyGroup.objects.create(name='Mi Grupo', creator=self.creator)
        resp = self.client.get(GROUPS_URI)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_invite_accepted_contact(self):
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        resp = self.client.post(f'{GROUPS_URI}{group.id}/invite/', {'padron': self.member1.padron})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['status'], GroupMembership.Status.PENDING)

    def test_invite_non_contact_returns_400(self):
        stranger = StudentFactory()
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        resp = self.client.post(f'{GROUPS_URI}{group.id}/invite/', {'padron': stranger.padron})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_self_returns_400(self):
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        resp = self.client.post(f'{GROUPS_URI}{group.id}/invite/', {'padron': self.creator.padron})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_invite_returns_409(self):
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        self.client.post(f'{GROUPS_URI}{group.id}/invite/', {'padron': self.member1.padron})
        resp = self.client.post(f'{GROUPS_URI}{group.id}/invite/', {'padron': self.member1.padron})
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_accept_invitation(self):
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        mem = GroupMembership.objects.create(group=group, student=self.member1)
        self.client.force_authenticate(user=self.member1.user)
        resp = self.client.post(f'{GROUPS_URI}{group.id}/accept/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], GroupMembership.Status.ACCEPTED)

    def test_leave_group(self):
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        GroupMembership.objects.create(group=group, student=self.member1, status='A')
        self.client.force_authenticate(user=self.member1.user)
        resp = self.client.delete(f'{GROUPS_URI}{group.id}/leave/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(GroupMembership.objects.filter(group=group, student=self.member1).exists())

    def test_schedule_returns_blocks_and_gaps(self):
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        GroupMembership.objects.create(group=group, student=self.member1, status='A')
        resp = self.client.get(f'{GROUPS_URI}{group.id}/schedule/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('members', resp.data)
        self.assertIn('blocks', resp.data)
        self.assertIn('free_gaps', resp.data)
        self.assertEqual(len(resp.data['members']), 2)

    def test_non_member_cannot_see_schedule(self):
        stranger = StudentFactory()
        group = StudyGroup.objects.create(name='Grupo', creator=self.creator)
        self.client.force_authenticate(user=stranger.user)
        resp = self.client.get(f'{GROUPS_URI}{group.id}/schedule/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        self.client.logout()
        resp = self.client.get(GROUPS_URI)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

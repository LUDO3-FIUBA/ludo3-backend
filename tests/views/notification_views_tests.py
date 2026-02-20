from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Notification, UserNotification
from tests.factories import UserFactory


class NotificationViewsTests(APITestCase):
    def setUp(self) -> None:
        self.sender = UserFactory()
        self.recipient_1 = UserFactory()
        self.recipient_2 = UserFactory()
        self.recipient_3 = UserFactory()

        self.create_notification_url = "/api/notifications/create_notification/"

    def test_create_notification_success(self):
        """
        Should create a notification and user notifications for all specified users.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "title": "Test notification",
            "message": "This is a test message",
            "user_ids": [self.recipient_1.id, self.recipient_2.id, self.recipient_3.id],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], data["title"])
        self.assertEqual(response.data["message"], data["message"])
        self.assertEqual(response.data["sender"], self.sender.id)

        # Verify DB state
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(UserNotification.objects.count(), 3)

        # All user notifications should be unread
        for un in UserNotification.objects.all():
            self.assertFalse(un.is_read)

    def test_create_notification_single_user(self):
        """
        Should create a notification for a single user.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "title": "Single user notification",
            "message": "Only for one user",
            "user_ids": [self.recipient_1.id],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserNotification.objects.count(), 1)
        self.assertEqual(UserNotification.objects.first().user, self.recipient_1)

    def test_create_notification_not_logged_in(self):
        """
        Should fail if unauthorized.
        """
        data = {
            "title": "Test",
            "message": "Test",
            "user_ids": [self.recipient_1.id],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_notification_missing_title(self):
        """
        Should return 400 if title is missing.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "message": "No title provided",
            "user_ids": [self.recipient_1.id],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_notification_missing_message(self):
        """
        Should return 400 if message is missing.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "title": "No message",
            "user_ids": [self.recipient_1.id],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("message", response.data)

    def test_create_notification_missing_user_ids(self):
        """
        Should return 400 if user_ids is missing.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "title": "No recipients",
            "message": "Missing user_ids",
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user_ids", response.data)

    def test_create_notification_empty_user_ids(self):
        """
        Should return 400 if user_ids is an empty list.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "title": "Empty recipients",
            "message": "No one to send to",
            "user_ids": [],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_notification_nonexistent_user_ids(self):
        """
        Should return 422 with the invalid user ids listed.
        """
        self.client.force_authenticate(user=self.sender)

        non_existent_id = 99999

        data = {
            "title": "Bad recipients",
            "message": "Some users don't exist",
            "user_ids": [self.recipient_1.id, non_existent_id],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn(non_existent_id, response.data["non_existent_user_ids"])

        # Verify nothing was created in the DB
        self.assertEqual(Notification.objects.count(), 0)
        self.assertEqual(UserNotification.objects.count(), 0)

    def test_create_notification_all_nonexistent_user_ids(self):
        """
        Should return 422 when all user ids are invalid.
        """
        self.client.force_authenticate(user=self.sender)

        data = {
            "title": "All bad",
            "message": "None exist",
            "user_ids": [88888, 99999],
        }

        response = self.client.post(self.create_notification_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(len(response.data["non_existent_user_ids"]), 2)

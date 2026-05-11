import io
import os
import tempfile
from unittest import mock

from django.test import SimpleTestCase

from backend.services.storage.aws import AwsS3StorageService
from backend.services.storage.base import StorageService
from backend.services.storage.gcs import GcsStorageService
from backend.services.storage.local import LocalStorageService


REQUIRED_METHODS = (
    'upload_b64_image',
    'upload_object',
    'download_object',
    'delete_object',
    'key_from_url',
    'presign_url',
)


class StorageInterfaceTests(SimpleTestCase):
    def test_all_providers_implement_full_interface(self):
        for cls in (LocalStorageService, AwsS3StorageService, GcsStorageService):
            for method in REQUIRED_METHODS:
                self.assertTrue(
                    callable(getattr(cls, method, None)),
                    f'{cls.__name__} is missing {method}',
                )

    def test_legacy_aws_s3_service_module_removed(self):
        with self.assertRaises(ModuleNotFoundError):
            __import__('backend.services.aws_s3_service')


class LocalStorageServiceTests(SimpleTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = mock.patch.dict(os.environ, {
            'LOCAL_MEDIA_ROOT': self.tmp.name,
            'LOCAL_MEDIA_URL': '/media/',
            'BASE_URL': 'http://localhost:8007',
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        self.storage = LocalStorageService()

    def test_upload_object_returns_absolute_url(self):
        url = self.storage.upload_object(io.BytesIO(b'hello'), 'models/abc.pdf')
        self.assertEqual(url, 'http://localhost:8007/media/models/abc.pdf')
        with open(os.path.join(self.tmp.name, 'models/abc.pdf'), 'rb') as f:
            self.assertEqual(f.read(), b'hello')

    def test_key_from_url_round_trips(self):
        url = self.storage.upload_object(io.BytesIO(b'x'), 'submissions/1/foo.pdf')
        self.assertEqual(self.storage.key_from_url(url), 'submissions/1/foo.pdf')

    def test_key_from_url_returns_none_for_external_urls(self):
        self.assertIsNone(self.storage.key_from_url('https://elsewhere.example/foo'))
        self.assertIsNone(self.storage.key_from_url(''))

    def test_presign_url_is_identity_for_local(self):
        url = 'http://localhost:8007/media/models/abc.pdf'
        self.assertEqual(self.storage.presign_url(url), url)
        self.assertIsNone(self.storage.presign_url(''))

    def test_delete_object_removes_file_and_tolerates_missing(self):
        self.storage.upload_object(io.BytesIO(b'bye'), 'tmp/del.pdf')
        full = os.path.join(self.tmp.name, 'tmp/del.pdf')
        self.assertTrue(os.path.exists(full))
        self.storage.delete_object('tmp/del.pdf')
        self.assertFalse(os.path.exists(full))
        self.storage.delete_object('tmp/never-existed.pdf')

    def test_satisfies_abstract_base(self):
        self.assertIsInstance(self.storage, StorageService)


class AwsS3StorageServiceTests(SimpleTestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {
            'AWS_ACCESS_KEY_ID': 'x',
            'AWS_SECRET_ACCESS_KEY': 'y',
            'AWS_BUCKET_NAME': 'my-bucket',
            'AWS_PUBLIC_READ_DOMAIN': 'my-bucket.s3.amazonaws.com',
        }, clear=False)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.boto = mock.patch('backend.services.storage.aws.boto3.client').start()
        self.addCleanup(mock.patch.stopall)
        self.client = self.boto.return_value
        self.storage = AwsS3StorageService()

    def test_delete_object_calls_s3(self):
        self.storage.delete_object('models/abc.pdf')
        self.client.delete_object.assert_called_once_with(
            Bucket='my-bucket', Key='models/abc.pdf',
        )

    def test_key_from_url_strips_bucket_prefix(self):
        url = 'https://my-bucket.s3.amazonaws.com/models/abc.pdf'
        self.assertEqual(self.storage.key_from_url(url), 'models/abc.pdf')
        self.assertIsNone(self.storage.key_from_url('https://other.example/x'))
        self.assertIsNone(self.storage.key_from_url(''))

    def test_presign_url_signs_owned_urls_and_passes_through_external(self):
        self.client.generate_presigned_url.return_value = 'https://signed.example/abc'
        url = 'https://my-bucket.s3.amazonaws.com/models/abc.pdf'
        self.assertEqual(self.storage.presign_url(url, expiration=120), 'https://signed.example/abc')
        self.client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={'Bucket': 'my-bucket', 'Key': 'models/abc.pdf'},
            ExpiresIn=120,
        )
        external = 'https://cms.example/file.pdf'
        self.assertEqual(self.storage.presign_url(external), external)
        self.assertIsNone(self.storage.presign_url(''))


class FormViewsImportTests(SimpleTestCase):
    def test_form_views_uses_new_storage_service(self):
        from backend.services import storage_service
        from backend.views import form_views

        self.assertIs(form_views.storage_service, storage_service)

import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def get_storage_settings():
    storage_provider = os.environ.get('STORAGE_PROVIDER', 'local').lower()
    if storage_provider not in ('local', 's3', 'gcs'):
        raise ValueError("STORAGE_PROVIDER must be one of: local, s3, gcs")

    storage_settings = {
        'STORAGE_PROVIDER': storage_provider,
    }

    if storage_provider == 'local':
        storage_settings.update(
            MEDIA_URL=os.environ.get('LOCAL_MEDIA_URL', '/media/'),
            DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
        )
        return storage_settings

    if storage_provider == 's3':
        aws_bucket_name = os.environ.get('AWS_BUCKET_NAME', '')
        if not aws_bucket_name:
            raise ValueError("AWS_BUCKET_NAME is required when STORAGE_PROVIDER=s3")

        s3_public_media = _as_bool(os.environ.get('AWS_S3_PUBLIC_MEDIA'), default=False)
        aws_querystring_expire = int(os.environ.get('AWS_QUERYSTRING_EXPIRE', '3600'))
        aws_public_read_domain = os.environ.get(
            'AWS_PUBLIC_READ_DOMAIN',
            f'{aws_bucket_name}.s3.amazonaws.com',
        ).rstrip('/')

        if aws_public_read_domain.startswith(('http://', 'https://')):
            aws_custom_domain = aws_public_read_domain.replace('https://', '').replace('http://', '')
            media_url = f'{aws_public_read_domain}/'
        else:
            aws_custom_domain = aws_public_read_domain
            media_url = f'https://{aws_public_read_domain}/'

        # For private buckets, keep URLs signed and avoid forcing a public custom domain.
        aws_s3_custom_domain = aws_custom_domain if s3_public_media else None

        storage_settings.update(
            AWS_STORAGE_BUCKET_NAME=aws_bucket_name,
            AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID', ''),
            AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY', ''),
            AWS_S3_ENDPOINT_URL=os.environ.get('AWS_ENDPOINT_URL', '') or None,
            AWS_S3_CUSTOM_DOMAIN=aws_s3_custom_domain,
            AWS_DEFAULT_ACL=None,
            AWS_QUERYSTRING_AUTH=not s3_public_media,
            AWS_QUERYSTRING_EXPIRE=aws_querystring_expire,
            AWS_S3_FILE_OVERWRITE=False,
            DEFAULT_FILE_STORAGE='storages.backends.s3boto3.S3Boto3Storage',
            MEDIA_URL=media_url,
        )
        return storage_settings

    gcs_bucket_name = os.environ.get('GCS_BUCKET_NAME', '')
    if not gcs_bucket_name:
        raise ValueError("GCS_BUCKET_NAME is required when STORAGE_PROVIDER=gcs")

    storage_settings.update(
        GS_BUCKET_NAME=gcs_bucket_name,
        GS_DEFAULT_ACL=None,
        GS_QUERYSTRING_AUTH=False,
        DEFAULT_FILE_STORAGE='storages.backends.gcloud.GoogleCloudStorage',
        MEDIA_URL=f'https://storage.googleapis.com/{gcs_bucket_name}/',
    )
    return storage_settings
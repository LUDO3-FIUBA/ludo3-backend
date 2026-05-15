import os
from datetime import timedelta


def _safe_basename(path):
    try:
        return os.path.basename(path)
    except Exception:
        return None


def presigned_download_url(file_field, request=None, expires=3600, filename=None):
    """Return a URL that forces download.

    - For S3: generate_presigned_url with ResponseContentDisposition
    - For GCS: generate_signed_url with response_disposition
    - Fallback: return absolute URL for local storage (uses `request` if provided)
    """
    if not file_field:
        return None

    storage = getattr(file_field, 'storage', None)
    name = getattr(file_field, 'name', None)
    if not storage or not name:
        return None

    disp = filename or _safe_basename(name) or name

    try:
        conn = getattr(storage, 'connection', None)
        bucket = getattr(storage, 'bucket_name', None)
        if conn is not None and bucket:
            client = conn.meta.client
            params = {
                'Bucket': bucket,
                'Key': name,
                'ResponseContentDisposition': f'attachment; filename="{disp}"',
            }
            return client.generate_presigned_url('get_object', Params=params, ExpiresIn=expires)
    except Exception:
        pass

    try:
        from google.cloud import storage as gcs

        bucket_name = getattr(storage, 'bucket_name', None)
        if not bucket_name:
            bucket_obj = getattr(storage, 'bucket', None)
            bucket_name = getattr(bucket_obj, 'name', None) if bucket_obj is not None else None

        if bucket_name:
            client = gcs.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(name)
            return blob.generate_signed_url(
                expiration=timedelta(seconds=expires),
                version='v4',
                response_disposition=f'attachment; filename="{disp}"',
            )
    except Exception:
        pass

    try:
        url = file_field.url
        if request and url and not url.startswith(('http://', 'https://')):
            return request.build_absolute_uri(url)
        return url
    except Exception:
        return None

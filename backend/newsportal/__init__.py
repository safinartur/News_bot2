# newsportal/__init__.py

import django.core.files.storage as storage_module
from django.conf import settings

# 🔧 Принудительно пересоздаём default_storage после загрузки settings
if not settings.DEBUG and getattr(settings, "DEFAULT_FILE_STORAGE", "").endswith("S3Boto3Storage"):
    from storages.backends.s3boto3 import S3Boto3Storage
    storage_module.default_storage = S3Boto3Storage()
    print("✅ Default storage switched to S3Boto3Storage (Cloudflare R2)")
else:
    print("ℹ️ Using local FileSystemStorage")

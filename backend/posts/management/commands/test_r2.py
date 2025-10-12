from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import traceback


class Command(BaseCommand):
    help = "Тестирует подключение к Cloudflare R2 через django-storages"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Тестируем Cloudflare R2...")

        try:
            # Проверим какой storage активен
            self.stdout.write(f"📦 DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
            self.stdout.write(f"🌍 ENDPOINT: {getattr(settings, 'AWS_S3_ENDPOINT_URL', 'N/A')}")
            self.stdout.write(f"🪣 BUCKET: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'N/A')}")

            # Пробуем создать тестовый файл
            test_filename = "covers/r2_test_upload.txt"
            content = ContentFile(b"Hello from Django R2 test!")

            path = default_storage.save(test_filename, content)
            url = default_storage.url(path)

            self.stdout.write(self.style.SUCCESS(f"✅ Файл успешно создан: {path}"))
            self.stdout.write(self.style.SUCCESS(f"🌐 Доступен по URL: {url}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR("❌ Ошибка при подключении к R2:"))
            self.stderr.write(str(e))
            traceback.print_exc()

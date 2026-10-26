"""
دانلود عکس‌های سربرگ صفحات داخلی از Unsplash در static/images/heads/.

    python manage.py fetch_header_images          # فقط عکس‌هایی که نیستند
    python manage.py fetch_header_images --force  # دانلود دوباره‌ی همه

پس از دانلود، فایل‌ها را در git ثبت کنید تا روی سرور هم از نسخه‌ی محلی
استفاده شود (روی سرور: collectstatic).
"""

import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.head_images import HEAD_IMAGES, cdn_url, static_path


class Command(BaseCommand):
    help = 'دانلود عکس‌های سربرگ صفحات داخلی از Unsplash'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='دانلود دوباره حتی اگر فایل موجود باشد')

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR) / 'static'
        ok = failed = 0
        for key, (photo_id, page, _caption) in HEAD_IMAGES.items():
            target = base / static_path(key)
            if target.exists() and not options['force']:
                self.stdout.write(f'  = {key}: موجود است')
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            request = urllib.request.Request(cdn_url(photo_id), headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = response.read()
            except Exception as exc:  # noqa: BLE001
                failed += 1
                self.stderr.write(f'  ✗ {key}: {exc}')
                continue
            if len(data) < 10_000:
                failed += 1
                self.stderr.write(f'  ✗ {key}: پاسخ نامعتبر ({len(data)} بایت)')
                continue
            target.write_bytes(data)
            ok += 1
            self.stdout.write(self.style.SUCCESS(f'  ✓ {key}: {len(data) // 1024} KB  ← {page}'))
        self.stdout.write(f'دانلود شد: {ok} — خطا: {failed}')

"""
بهینه‌سازی سبک تصاویر آپلودی.

هدف: جلوگیری از قرار گرفتن فایل‌های چند مگابایتی روی سایت، بدون اضافه کردن
هیچ وابستگی جدید (فقط Pillow که از قبل برای ImageField لازم است).

این ماژول هرگز خطا پرتاب نمی‌کند؛ اگر فایل قابل پردازش نبود، فایل اصلی
دست‌نخورده ذخیره می‌شود.
"""

from __future__ import annotations

import os
from io import BytesIO

from django.core.files.base import ContentFile

MAX_WIDTH = 1920
MAX_HEIGHT = 1920
QUALITY = 82

# فرمت‌هایی که بازنویسی آن‌ها بی‌خطر است. GIF (احتمال انیمیشن) و SVG کنار گذاشته می‌شوند.
SAFE_FORMATS = {'JPEG', 'JPG', 'PNG', 'WEBP'}


def _save_kwargs(fmt: str) -> dict:
    if fmt in {'JPEG', 'JPG'}:
        return {'format': 'JPEG', 'quality': QUALITY, 'optimize': True, 'progressive': True}
    if fmt == 'WEBP':
        return {'format': 'WEBP', 'quality': QUALITY, 'method': 6}
    return {'format': 'PNG', 'optimize': True}


def optimize_image_field(fieldfile, max_width: int = MAX_WIDTH, max_height: int = MAX_HEIGHT) -> None:
    """
    اگر فایل تازه آپلود شده باشد، آن را بازچینی (چرخش EXIF)، محدود به ابعاد
    حداکثری و فشرده می‌کند و نتیجه را در جای همان فیلد می‌نشاند.
    """
    if not fieldfile or getattr(fieldfile, '_committed', True):
        return

    try:
        from PIL import Image, ImageOps
    except ImportError:  # pragma: no cover - Pillow همراه پروژه نصب است
        return

    replaced = False
    try:
        fieldfile.open()
        fieldfile.seek(0)
        image = Image.open(fieldfile)
        fmt = (image.format or '').upper()
        if fmt not in SAFE_FORMATS:
            return

        image = ImageOps.exif_transpose(image)
        needs_resize = image.width > max_width or image.height > max_height
        if needs_resize:
            image.thumbnail((max_width, max_height), Image.LANCZOS)

        if fmt in {'JPEG', 'JPG'} and image.mode not in {'RGB', 'L'}:
            image = image.convert('RGB')

        buffer = BytesIO()
        image.save(buffer, **_save_kwargs(fmt))
        optimized = buffer.getvalue()

        # اگر فشرده‌سازی سود معناداری نداشت و تغییر ابعادی هم لازم نبود، فایل اصلی می‌ماند.
        original_size = getattr(fieldfile, 'size', None) or len(optimized) + 1
        if not needs_resize and len(optimized) >= original_size * 0.95:
            return

        name = os.path.basename(fieldfile.name)
        fieldfile.save(name, ContentFile(optimized), save=False)
        replaced = True
    except Exception:
        # هر فایل مشکل‌دار یا فرمت غیرمنتظره: بدون تغییر عبور می‌کنیم.
        return
    finally:
        if replaced:
            # فایل جایگزین شد و _committed=True است؛ Django دیگر سراغ
            # فایل اصلی نمی‌رود، پس بستنش بی‌خطر است.
            try:
                fieldfile.close()
            except Exception:
                pass
        else:
            # جایگزین نشد؛ _committed هنوز False است و Django خودش بعداً
            # از همین فایل آپلودی اصلی chunks() می‌گیرد. پس نباید ببندیمش،
            # فقط باید موقعیت خواندن را برگردانیم.
            try:
                fieldfile.seek(0)
            except Exception:
                pass


class OptimizedImagesMixin:
    """
    میکسین مدل: نام فیلدهای تصویری را در `OPTIMIZED_IMAGE_FIELDS` بنویسید تا
    هنگام ذخیره، به‌صورت خودکار بهینه شوند.
    """

    OPTIMIZED_IMAGE_FIELDS: tuple[str, ...] = ()

    def save(self, *args, **kwargs):
        for field_name in self.OPTIMIZED_IMAGE_FIELDS:
            optimize_image_field(getattr(self, field_name, None))
        return super().save(*args, **kwargs)
from functools import lru_cache

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

from core.head_images import HEAD_IMAGES, cdn_url, static_path

register = template.Library()


@lru_cache(maxsize=None)
def _local_exists(path):
    return bool(finders.find(path))


@register.simple_tag
def head_image(key):
    """نشانی عکس سربرگ: فایل محلی اگر دانلود شده باشد، وگرنه CDN آن‌اسپلش."""
    if not key or key not in HEAD_IMAGES:
        return ''
    path = static_path(key)
    if _local_exists(path):
        return static(path)
    return cdn_url(HEAD_IMAGES[key][0])

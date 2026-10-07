"""
میان‌افزارهای سایت.
"""

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class DefaultLanguageMiddleware:
    """
    زبان پیش‌فرض سایت همیشه فارسی (LANGUAGE_CODE) باشد.

    LocaleMiddleware برای نشانی‌های بدون پیشوند زبان (مثل «/») به‌ترتیب به
    کوکی زبان، سرآیند Accept-Language مرورگر و در آخر LANGUAGE_CODE نگاه
    می‌کند؛ پس بازدیدکننده‌ای با مرورگر انگلیسی به /en/ هدایت می‌شد. این
    میان‌افزار سرآیند مرورگر را نادیده می‌گیرد: تا کاربر خودش زبان را با دکمه‌ی
    تغییر زبان (کوکی django_language) عوض نکرده، سایت فارسی باز می‌شود.

    باید پیش از django.middleware.locale.LocaleMiddleware قرار بگیرد.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.META.pop('HTTP_ACCEPT_LANGUAGE', None)
        return self.get_response(request)


class AliasDomainRedirectMiddleware:
    """
    دامنه‌های فرعی (مثلاً atlasaim.ir) با ریدایرکت دائمی ۳۰۱ به دامنه‌ی اصلی
    (www.atlas-aim.com) با همان مسیر فرستاده می‌شوند — یک نشانی واحد برای گوگل.

    باید پیش از SecurityMiddleware بیاید: آن میان‌افزار برای ریدایرکت HTTPS
    نام دامنه را اعتبارسنجی می‌کند و دامنه‌ی فرعی را با خطای ۴۰۰ رد می‌کرد.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.aliases = {d.lower() for d in getattr(settings, 'SITE_ALIAS_DOMAINS', ())}
        self.target = settings.SITE_URL.rstrip('/')

    def __call__(self, request):
        host = request.META.get('HTTP_HOST', '').split(':')[0].lower()
        if host in self.aliases:
            return HttpResponsePermanentRedirect(self.target + request.get_full_path())
        return self.get_response(request)

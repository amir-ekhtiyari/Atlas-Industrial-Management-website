"""
میان‌افزارهای سایت.
"""


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

from django.conf import settings
from django.urls import Resolver404, resolve, reverse
from django.utils import translation

from .utils import get_company


def company_info(request):
    """
    اطلاعات شرکت (لوگو، تماس، شبکه‌های اجتماعی) را در تمام تمپلیت‌ها
    زیر نام global_company در دسترس قرار می‌دهد. این‌طوری هدر و فوتر
    مستقل از این‌که هر View چه چیزی pass کرده، به این اطلاعات دسترسی دارند.
    """
    return {'global_company': get_company(request)}


def _translated_path(request, language_code):
    """
    نشانی صفحه‌ی فعلی را در زبان دیگر می‌سازد (برای دکمه تغییر زبان و hreflang).
    اگر مسیر قابل تفکیک نبود، به صفحه اصلی همان زبان برمی‌گردیم.
    """
    match = getattr(request, 'resolver_match', None)
    if match is None:
        try:
            match = resolve(request.path_info)
        except Resolver404:
            match = None

    if match is not None:
        try:
            with translation.override(language_code):
                path = reverse(match.view_name, args=match.args, kwargs=match.kwargs)
            query = request.META.get('QUERY_STRING', '')
            return f'{path}?{query}' if query else path
        except Exception:
            pass

    with translation.override(language_code):
        return reverse('core:home')


def site_context(request):
    """
    داده‌های مشترک هدر/فوتر:
    - `site_languages` / `other_language`: تغییر زبان و تگ‌های hreflang.
    - `footer_lines`: خطوط محصول برای ستون فوتر — از دیتابیس، پس افزودن خط
      تازه بدون تغییر قالب در فوتر دیده می‌شود.

    کوئری خطوط محصول فقط برای صفحات سایت اجرا می‌شود، نه پنل مدیریت.
    """
    is_admin = request.path.startswith('/admin/')
    current = translation.get_language() or settings.LANGUAGE_CODE

    languages = []
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name,
            'is_current': code == current,
            'path': '' if is_admin else _translated_path(request, code),
        })
    other = next((lang for lang in languages if not lang['is_current']), None)

    footer_lines = []
    if not is_admin:
        from django.db.models import Count, Q
        from products.models import Category
        footer_lines = list(
            Category.objects
            .annotate(live=Count('products', filter=Q(products__is_active=True)))
            .filter(live__gt=0)
            .only('name', 'slug')[:3]
        )

    return {
        'site_languages': languages,
        'other_language': other,
        'current_language_code': current,
        'footer_lines': footer_lines,
    }

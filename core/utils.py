"""
دسترسی مشترک به اطلاعات شرکت.

`CompanyInfo` در هر صفحه هم توسط context processor (برای هدر و فوتر) و هم
توسط بعضی View‌ها لازم است. این تابع نتیجه را روی خود request نگه می‌دارد
تا در هر درخواست فقط یک کوئری اجرا شود.
"""

from django.http import Http404

from .models import CompanyInfo

_CACHE_ATTR = '_atlas_company_info'


def get_company(request=None):
    """اطلاعات شرکت را برمی‌گرداند؛ اگر رکوردی نباشد، None."""
    if request is None:
        return CompanyInfo.objects.first()

    if not hasattr(request, _CACHE_ATTR):
        setattr(request, _CACHE_ATTR, CompanyInfo.objects.first())
    return getattr(request, _CACHE_ATTR)


def get_company_or_404(request):
    """برای صفحاتی که بدون اطلاعات شرکت معنا ندارند (خانه، درباره ما، خدمات)."""
    company = get_company(request)
    if company is None:
        raise Http404('اطلاعات شرکت ثبت نشده است.')
    return company

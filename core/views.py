import io

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

from news.models import Post
from products.models import Category, Product
from team.models import TeamMember

from .models import (
    Advantage,
    Capability,
    Certification,
    FAQ,
    Industry,
    Milestone,
    ProcessStep,
    Service,
    Statistic,
    Technology,
    Testimonial,
)
from .utils import get_company_or_404


def _featured_products(limit=3):
    """
    محصولات شاخص برای صفحه اصلی. اگر هیچ محصولی «شاخص» علامت نخورده باشد،
    تازه‌ترین محصولات فعال جای آن را می‌گیرند تا بخش خالی نماند.
    """
    base = Product.objects.active().with_related()
    featured = list(base.filter(is_featured=True)[:limit])
    if len(featured) < limit:
        seen = {p.pk for p in featured}
        for product in base.exclude(pk__in=seen)[: limit - len(featured)]:
            featured.append(product)
    return featured


def home(request):
    company = get_company_or_404(request)

    context = {
        'company': company,
        'technologies': Technology.objects.active()[:6],
        'industries': Industry.objects.active()[:4],
        'featured_products': _featured_products(),
        'product_lines': (
            Category.objects
            .annotate(live=Count('products', filter=Q(products__is_active=True)))
            .filter(live__gt=0)
        ),
        'product_total': Product.objects.active().count(),
        'advantages': Advantage.objects.active(),
        'capabilities': Capability.objects.active()[:6],
        'certifications': Certification.objects.active(),
        'statistics': Statistic.objects.active()[:4],
        'testimonials': Testimonial.objects.active()[:3],
        'latest_posts': Post.objects.published().with_related()[:3],
    }
    return render(request, 'core/home.html', context)


def about(request):
    company = get_company_or_404(request)
    context = {
        'company': company,
        'milestones': Milestone.objects.active(),
        'capabilities': Capability.objects.active(),
        'certifications': Certification.objects.active(),
        'statistics': Statistic.objects.active(),
        'process_steps': ProcessStep.objects.active(),
        'team_members': TeamMember.objects.filter(is_active=True)[:4],
        'testimonials': Testimonial.objects.active()[:3],
        'technologies': Technology.objects.active()[:6],
    }
    return render(request, 'core/about.html', context)


def technology_list(request):
    company = get_company_or_404(request)
    context = {
        'company': company,
        'technologies': Technology.objects.active().prefetch_related(
            Prefetch('products', queryset=Product.objects.active().only('name', 'slug'))
        ),
        'capabilities': Capability.objects.active(),
        'process_steps': ProcessStep.objects.active(),
        'services': Service.objects.active(),
    }
    return render(request, 'core/technology_list.html', context)


def technology_detail(request, slug):
    technology = get_object_or_404(Technology.objects.active(), slug=slug)
    context = {
        'company': get_company_or_404(request),
        'item': technology,
        'kind': 'technology',
        'related_products': technology.products.filter(is_active=True).with_related()[:3],
        'siblings': Technology.objects.active().exclude(pk=technology.pk)[:4],
    }
    return render(request, 'core/page_detail.html', context)


def industry_list(request):
    company = get_company_or_404(request)
    context = {
        'company': company,
        'industries': Industry.objects.active().prefetch_related(
            Prefetch('products', queryset=Product.objects.active().only('name', 'slug'))
        ),
        'technologies': Technology.objects.active()[:6],
    }
    return render(request, 'core/industry_list.html', context)


def industry_detail(request, slug):
    industry = get_object_or_404(Industry.objects.active(), slug=slug)
    context = {
        'company': get_company_or_404(request),
        'item': industry,
        'kind': 'industry',
        'related_products': industry.products.filter(is_active=True).with_related()[:3],
        'siblings': Industry.objects.active().exclude(pk=industry.pk)[:4],
    }
    return render(request, 'core/page_detail.html', context)


def quality(request):
    company = get_company_or_404(request)
    context = {
        'company': company,
        'capabilities': Capability.objects.active(),
        'certifications': Certification.objects.active(),
        'process_steps': ProcessStep.objects.active(),
        'services': Service.objects.active(),
        'faqs': FAQ.objects.active(),
    }
    return render(request, 'core/quality.html', context)


@require_GET
def robots_txt(request):
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Allow: /',
        '',
        f'Sitemap: {sitemap_url}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


@require_GET
def qr_code(request):
    """
    QR کد آدرس سایت (`settings.SITE_URL`). یک‌بار می‌سازد و در کش نگه می‌دارد؛
    با تغییر SITE_URL (مثلاً هنگام تنظیم دامنه‌ی واقعی) کلید کش هم عوض می‌شود.
    """
    cache_key = f'site-qr-png:{settings.SITE_URL}'
    png_bytes = cache.get(cache_key)
    if png_bytes is None:
        import qrcode
        image = qrcode.make(settings.SITE_URL)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()
        cache.set(cache_key, png_bytes, None)

    response = HttpResponse(png_bytes, content_type='image/png')
    disposition = 'attachment' if request.GET.get('download') else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="atlas-qr.png"'
    return response


def error_404(request, exception=None):
    return render(request, '404.html', status=404)


def error_500(request):
    # بدون context processor رندر می‌شود: هنگام خطای سرور ممکن است دیتابیس
    # در دسترس نباشد و اجرای پردازنده‌های context خودش خطای تازه بسازد.
    return HttpResponse(render_to_string('500.html'), status=500)

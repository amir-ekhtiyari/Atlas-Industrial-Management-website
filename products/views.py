from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, render

from core.models import Industry, Technology
from .models import Category, Product, ProductImage

PAGE_SIZE = 9


def product_list(request):
    """
    کاتالوگ محصولات — مستقل از هر محصول خاص.

    فیلترها روی «خط محصول»، «حوزه فناوری» و «صنعت» کار می‌کنند؛ همه از
    دیتابیس می‌آیند، پس افزودن خط یا صنعت تازه از پنل مدیریت بلافاصله در
    این صفحه دیده می‌شود.
    """
    products = Product.objects.active().with_related()

    line_slug = (request.GET.get('line') or '').strip()
    tech_slug = (request.GET.get('technology') or '').strip()
    industry_slug = (request.GET.get('industry') or '').strip()
    query = (request.GET.get('q') or '').strip()

    active_line = active_tech = active_industry = None

    if line_slug:
        active_line = Category.objects.filter(slug=line_slug).first()
        if active_line:
            products = products.filter(category=active_line)

    if tech_slug:
        active_tech = Technology.objects.filter(slug=tech_slug).first()
        if active_tech:
            products = products.filter(technologies=active_tech)

    if industry_slug:
        active_industry = Industry.objects.filter(slug=industry_slug).first()
        if active_industry:
            products = products.filter(industries=active_industry)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(model_code__icontains=query)
        )

    products = products.distinct()
    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))

    live = Q(products__is_active=True)
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'product_lines': (
            Category.objects.annotate(live=Count('products', filter=live)).filter(live__gt=0)
        ),
        'technologies': (
            Technology.objects.active()
            .annotate(live=Count('products', filter=live)).filter(live__gt=0)
        ),
        'industries': (
            Industry.objects.active()
            .annotate(live=Count('products', filter=live)).filter(live__gt=0)
        ),
        'active_line': active_line,
        'active_technology': active_tech,
        'active_industry': active_industry,
        'query': query,
        'has_filters': bool(active_line or active_tech or active_industry or query),
        'total_count': paginator.count,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    صفحه‌ی محصول — قالب یکسان برای هر محصولی که در پنل ساخته شود.
    بخش‌هایی که داده ندارند به‌طور خودکار حذف می‌شوند.
    """
    product = get_object_or_404(
        Product.objects
        .active()
        .select_related('category')
        .prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.order_by('order', 'id')),
            'specs', 'features', 'applications', 'documents',
            'technologies', 'industries',
        ),
        slug=slug,
    )

    specs = list(product.specs.all())
    technologies = list(product.technologies.all())

    related = Product.objects.active().with_related().exclude(pk=product.pk)
    tech_ids = [t.pk for t in technologies]
    if product.category_id and tech_ids:
        related = related.filter(
            Q(category_id=product.category_id) | Q(technologies__in=tech_ids)
        ).distinct()
    elif product.category_id:
        related = related.filter(category_id=product.category_id)
    elif tech_ids:
        related = related.filter(technologies__in=tech_ids).distinct()

    context = {
        'product': product,
        'gallery': list(product.images.all()),
        'specs': specs,
        'highlight_specs': [s for s in specs if s.is_highlight][:4],
        'features': list(product.features.all()),
        'applications': list(product.applications.all()),
        'documents': list(product.documents.all()),
        'technologies': technologies,
        'industries': list(product.industries.all()),
        'related_products': related[:3],
    }
    return render(request, 'products/product_detail.html', context)

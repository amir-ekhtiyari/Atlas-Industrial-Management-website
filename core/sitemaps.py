from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from news.models import Post
from products.models import Product

from .models import Industry, Technology


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'monthly'
    i18n = True

    def items(self):
        return [
            'core:home',
            'core:about',
            'core:technology_list',
            'core:industry_list',
            'core:quality',
            'products:list',
            'news:list',
            'team:list',
            'contact:form',
        ]

    def location(self, item):
        return reverse(item)

    def priority_for(self, item):  # pragma: no cover - سازگاری با نسخه‌های آینده
        return 1.0 if item == 'core:home' else self.priority


class ProductSitemap(Sitemap):
    priority = 0.9
    changefreq = 'weekly'
    i18n = True

    def items(self):
        return Product.objects.active()

    def lastmod(self, obj):
        return obj.updated_at


class TechnologySitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'
    i18n = True

    def items(self):
        # فقط مواردی که متن کامل دارند صفحه‌ی مستقل دارند.
        return [t for t in Technology.objects.active() if t.has_page]


class IndustrySitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'
    i18n = True

    def items(self):
        return [i for i in Industry.objects.active() if i.has_page]


class PostSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'
    i18n = True

    def items(self):
        return Post.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'technologies': TechnologySitemap,
    'industries': IndustrySitemap,
    'insights': PostSitemap,
}

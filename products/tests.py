from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from core.models import Industry, Technology
from core.tests import make_company, make_industry, make_technology

from .models import (
    Category,
    Product,
    ProductApplication,
    ProductFeature,
    ProductImage,
    ProductSpecification,
)


def make_product(**overrides):
    """
    ساخت محصول تست. اگر `name` بدهید، ترجمه‌های فارسی/انگلیسی هم با همان مقدار
    پر می‌شوند تا کوئری‌های modeltranslation در هر دو زبان کار کنند.
    """
    data = {
        'name': 'تجهیز نمونه',
        'short_description': 'توضیح کوتاه',
        'description': 'توضیح کامل',
    }
    data.update(overrides)
    for field in ('name', 'short_description', 'description'):
        value = data[field]
        data.setdefault(f'{field}_fa', value)
        data.setdefault(f'{field}_en', value)
    return Product.objects.create(**data)


def make_line(**overrides):
    data = {'name': 'خط نمونه', 'name_fa': 'خط نمونه', 'name_en': 'Sample line', 'slug': 'sample-line'}
    data.update(overrides)
    return Category.objects.create(**data)


class ProductModelTests(TestCase):
    def test_slug_is_generated_from_name(self):
        product = make_product(name='ایستگاه تنظیم فشار')
        self.assertTrue(product.slug)
        self.assertEqual(product.get_absolute_url(),
                         reverse('products:detail', kwargs={'slug': product.slug}))

    def test_explicit_slug_is_respected(self):
        self.assertEqual(make_product(slug='atlas-unit-a').slug, 'atlas-unit-a')

    def test_image_is_optional(self):
        self.assertFalse(make_product().image)

    def test_meta_description_falls_back_to_short_description(self):
        product = make_product()
        self.assertEqual(product.display_meta_description, product.short_description)
        product.meta_description = 'توضیح سئو'
        self.assertEqual(product.display_meta_description, 'توضیح سئو')

    def test_active_queryset_excludes_hidden_products(self):
        make_product(slug='visible')
        make_product(slug='hidden', is_active=False)
        self.assertEqual([p.slug for p in Product.objects.active()], ['visible'])

    def test_specification_display_value_joins_unit(self):
        product = make_product()
        spec = ProductSpecification.objects.create(
            product=product, label='فشار', value='4', unit='بار')
        self.assertEqual(spec.display_value, '4 بار')

    def test_specification_without_unit_has_clean_value(self):
        spec = ProductSpecification.objects.create(
            product=make_product(), label='ولتاژ', value='220V')
        self.assertEqual(spec.display_value, '220V')

    def test_gallery_alt_text_falls_back_to_product_name(self):
        product = make_product()
        image = ProductImage.objects.create(product=product, image='products/gallery/a.png')
        self.assertEqual(image.alt_text, product.name)
        image.caption = 'نمای جلو'
        self.assertEqual(image.alt_text, 'نمای جلو')

    def test_product_links_to_technologies_and_industries(self):
        """
        محصول باید بتواند به چند فناوری و صنعت وصل شود؛ همین ارتباط است که
        اجازه می‌دهد محصول تازه بدون تغییر کد در صفحات مربوطه دیده شود.
        """
        product = make_product()
        tech = make_technology(slug='gas-systems')
        industry = make_industry(slug='aviation')
        product.technologies.add(tech)
        product.industries.add(industry)
        self.assertEqual(list(tech.products.all()), [product])
        self.assertEqual(list(industry.products.all()), [product])

    def test_line_absolute_url_filters_catalogue(self):
        line = make_line(slug='gas-systems-line')
        self.assertIn('line=gas-systems-line', line.get_absolute_url())


class ProductListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        make_company()
        cls.line_a = make_line(slug='aviation-safety', name='ایمنی هوانوردی',
                               name_fa='ایمنی هوانوردی', name_en='Aviation safety')
        cls.line_b = make_line(slug='gas-systems', name='سیستم‌های گاز',
                               name_fa='سیستم‌های گاز', name_en='Gas systems')
        cls.tech = make_technology(slug='pressurised-gas')
        cls.industry = make_industry(slug='aviation')

        cls.p1 = make_product(slug='unit-a', name='واحد الف', category=cls.line_a,
                              model_code='ATL-A')
        cls.p1.technologies.add(cls.tech)
        cls.p1.industries.add(cls.industry)

        cls.p2 = make_product(slug='unit-b', name='واحد ب', category=cls.line_b)
        cls.p2.technologies.add(cls.tech)

        make_product(slug='hidden-unit', name='پنهان', is_active=False)

    def test_list_shows_only_active_products(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)
        slugs = [p.slug for p in response.context['products']]
        self.assertNotIn('hidden-unit', slugs)
        self.assertEqual(len(slugs), 2)

    def test_filter_by_product_line(self):
        response = self.client.get(reverse('products:list'), {'line': 'gas-systems'})
        self.assertEqual(response.context['active_line'], self.line_b)
        self.assertEqual([p.slug for p in response.context['products']], ['unit-b'])

    def test_filter_by_technology(self):
        response = self.client.get(reverse('products:list'), {'technology': 'pressurised-gas'})
        self.assertEqual(response.context['active_technology'], self.tech)
        self.assertEqual(len(response.context['products']), 2)

    def test_filter_by_industry(self):
        response = self.client.get(reverse('products:list'), {'industry': 'aviation'})
        self.assertEqual(response.context['active_industry'], self.industry)
        self.assertEqual([p.slug for p in response.context['products']], ['unit-a'])

    def test_unknown_filter_value_is_ignored(self):
        response = self.client.get(reverse('products:list'), {'line': 'nope', 'technology': 'nope'})
        self.assertIsNone(response.context['active_line'])
        self.assertIsNone(response.context['active_technology'])
        self.assertEqual(len(response.context['products']), 2)

    def test_search_matches_name_or_model_code(self):
        by_name = self.client.get(reverse('products:list'), {'q': 'واحد ب'})
        self.assertEqual([p.slug for p in by_name.context['products']], ['unit-b'])
        by_code = self.client.get(reverse('products:list'), {'q': 'ATL-A'})
        self.assertEqual([p.slug for p in by_code.context['products']], ['unit-a'])

    def test_facets_exclude_empty_groups(self):
        make_line(slug='empty-line', name='خالی', name_fa='خالی')
        make_technology(slug='unused-tech', title='بی‌استفاده', title_fa='بی‌استفاده')
        response = self.client.get(reverse('products:list'))
        self.assertNotIn('empty-line', {c.slug for c in response.context['product_lines']})
        self.assertNotIn('unused-tech', {t.slug for t in response.context['technologies']})

    def test_has_filters_flag(self):
        self.assertFalse(self.client.get(reverse('products:list')).context['has_filters'])
        self.assertTrue(
            self.client.get(reverse('products:list'), {'q': 'x'}).context['has_filters'])


class ProductDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        make_company()
        cls.line = make_line(slug='gas-systems')
        cls.tech = make_technology(slug='pressurised-gas', body='متن فناوری')
        cls.industry = make_industry(slug='aviation', body='متن صنعت')

        cls.product = make_product(slug='unit-a', category=cls.line, model_code='ATL-A')
        cls.product.technologies.add(cls.tech)
        cls.product.industries.add(cls.industry)

        cls.sibling = make_product(slug='unit-b', name='واحد ب', category=cls.line)

        ProductSpecification.objects.create(
            product=cls.product, group='عملکرد', label='فشار', value='4',
            unit='بار', is_highlight=True, order=1)
        ProductSpecification.objects.create(
            product=cls.product, group='ابعاد', label='وزن', value='12',
            unit='کیلوگرم', order=2)
        ProductFeature.objects.create(product=cls.product, title='پایداری', order=1)
        ProductApplication.objects.create(product=cls.product, title='خط تأمین', order=1)
        ProductImage.objects.create(product=cls.product, image='products/gallery/a.png', order=1)

    def test_detail_exposes_all_related_collections(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['specs']), 2)
        self.assertEqual(len(response.context['features']), 1)
        self.assertEqual(len(response.context['applications']), 1)
        self.assertEqual(len(response.context['gallery']), 1)
        self.assertEqual(len(response.context['technologies']), 1)
        self.assertEqual(len(response.context['industries']), 1)

    def test_highlight_specs_only_include_flagged_rows(self):
        response = self.client.get(self.product.get_absolute_url())
        highlights = response.context['highlight_specs']
        self.assertEqual(len(highlights), 1)
        self.assertEqual(highlights[0].label, 'فشار')

    def test_related_products_share_line_or_technology(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual([p.slug for p in response.context['related_products']], ['unit-b'])

    def test_detail_works_for_bare_product(self):
        """محصول بدون تصویر، مشخصات، فناوری یا صنعت هم باید درست رندر شود."""
        bare = make_product(slug='bare-unit', name='واحد ساده')
        response = self.client.get(bare.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['specs'], [])
        self.assertEqual(response.context['technologies'], [])

    def test_inactive_product_returns_404(self):
        hidden = make_product(slug='hidden-unit', is_active=False)
        self.assertEqual(self.client.get(hidden.get_absolute_url()).status_code, 404)

    def test_detail_query_count_does_not_grow_with_data(self):
        """جلوگیری از بازگشت مشکل N+1: تعداد کوئری باید مستقل از حجم داده بماند."""
        with CaptureQueriesContext(connection) as baseline:
            self.client.get(self.product.get_absolute_url())

        for index in range(6):
            ProductSpecification.objects.create(
                product=self.product, label=f'مشخصه {index}', value=str(index), order=index + 10)
            ProductImage.objects.create(
                product=self.product, image=f'products/gallery/{index}.png', order=index + 10)
            ProductFeature.objects.create(
                product=self.product, title=f'ویژگی {index}', order=index + 10)

        with self.assertNumQueries(len(baseline.captured_queries)):
            self.client.get(self.product.get_absolute_url())

from django.test import TestCase
from django.urls import reverse

from core.models import (
    Advantage,
    Capability,
    Certification,
    CompanyInfo,
    FAQ,
    Industry,
    Milestone,
    ProcessStep,
    Service,
    Statistic,
    Technology,
    Testimonial,
)


def make_company(**overrides):
    """
    ساخت رکورد اطلاعات شرکت برای تست.
    `CompanyInfo.save` عمداً full_clean صدا می‌زند، پس در تست از save مدل
    پایه استفاده می‌کنیم تا نیازی به فایل تصویری واقعی نباشد.
    """
    data = {
        'name': 'اطلس', 'name_fa': 'اطلس', 'name_en': 'Atlas',
        'hero_text': 'متن معرفی', 'hero_text_fa': 'متن معرفی', 'hero_text_en': 'Intro text',
        'about_text': 'درباره ما', 'about_text_fa': 'درباره ما', 'about_text_en': 'About us',
        'intro_text': 'معرفی', 'intro_text_fa': 'معرفی', 'intro_text_en': 'Company intro',
        'address': 'ایران', 'address_fa': 'ایران', 'address_en': 'Iran',
        'phone': '02100000000',
        'email': 'info@example.com',
    }
    data.update(overrides)
    company = CompanyInfo(**data)
    super(CompanyInfo, company).save()
    return company


def make_technology(**overrides):
    data = {'title': 'سیستم‌های گاز', 'title_fa': 'سیستم‌های گاز', 'title_en': 'Gas systems'}
    data.update(overrides)
    return Technology.objects.create(**data)


def make_industry(**overrides):
    data = {'title': 'هوانوردی', 'title_fa': 'هوانوردی', 'title_en': 'Aviation'}
    data.update(overrides)
    return Industry.objects.create(**data)


class CompanyInfoModelTests(TestCase):
    def test_singleton_blocks_second_record(self):
        make_company()
        second = CompanyInfo(
            name='دیگر', hero_text='x', about_text='y',
            address='z', phone='1', email='a@b.com',
        )
        with self.assertRaises(Exception):
            second.save()

    def test_display_hero_title_falls_back_to_name(self):
        company = make_company()
        self.assertEqual(company.display_hero_title, company.name)
        company.hero_title = 'تیتر اختصاصی'
        self.assertEqual(company.display_hero_title, 'تیتر اختصاصی')

    def test_social_links_only_returns_filled_urls(self):
        company = make_company(linkedin_url='https://linkedin.test/atlas')
        links = company.social_links
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]['icon'], 'icon-linkedin')
        self.assertTrue(company.has_social_links)

    def test_company_without_socials_reports_none(self):
        company = make_company()
        self.assertEqual(company.social_links, [])
        self.assertFalse(company.has_social_links)

    def test_logo_is_optional(self):
        company = make_company()
        self.assertFalse(company.logo)


class PageContentTests(TestCase):
    """رفتار مشترک مدل‌های دارای صفحه‌ی اختصاصی (فناوری و صنعت)."""

    def test_slug_is_generated_from_title(self):
        tech = make_technology(title='آزمون و کنترل کیفیت', title_fa='آزمون و کنترل کیفیت')
        self.assertTrue(tech.slug)
        self.assertEqual(tech.get_absolute_url(),
                         reverse('core:technology_detail', kwargs={'slug': tech.slug}))

    def test_explicit_slug_is_respected(self):
        tech = make_technology(slug='gas-systems')
        self.assertEqual(tech.slug, 'gas-systems')

    def test_has_page_requires_body(self):
        tech = make_technology(slug='no-body')
        self.assertFalse(tech.has_page)
        tech.body = 'متن کامل'
        self.assertTrue(tech.has_page)

    def test_meta_description_falls_back_to_description(self):
        tech = make_technology(slug='meta', description='توضیح کوتاه')
        self.assertEqual(tech.display_meta_description, 'توضیح کوتاه')
        tech.meta_description = 'سئو'
        self.assertEqual(tech.display_meta_description, 'سئو')

    def test_industry_url_uses_industry_route(self):
        industry = make_industry(slug='aviation')
        self.assertEqual(industry.get_absolute_url(),
                         reverse('core:industry_detail', kwargs={'slug': 'aviation'}))

    def test_active_manager_filters_inactive(self):
        make_technology(slug='live')
        make_technology(slug='hidden', title='پنهان', title_fa='پنهان', is_active=False)
        self.assertEqual([t.slug for t in Technology.objects.active()], ['live'])

    def test_default_ordering_uses_order_field(self):
        make_technology(slug='second', title='دو', title_fa='دو', order=20)
        make_technology(slug='first', title='یک', title_fa='یک', order=10)
        self.assertEqual([t.slug for t in Technology.objects.all()], ['first', 'second'])


class OrderedContentTests(TestCase):
    def test_active_manager_filters_inactive(self):
        Advantage.objects.create(title='فعال', order=1)
        Advantage.objects.create(title='غیرفعال', order=2, is_active=False)
        self.assertEqual([a.title for a in Advantage.objects.active()], ['فعال'])

    def test_default_ordering_uses_order_field(self):
        Capability.objects.create(title='دو', order=20)
        Capability.objects.create(title='یک', order=10)
        self.assertEqual([c.title for c in Capability.objects.all()], ['یک', 'دو'])


class CoreViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = make_company()
        cls.tech = make_technology(slug='gas-systems', body='متن کامل فناوری')
        cls.tech_no_page = make_technology(
            slug='no-page', title='بدون صفحه', title_fa='بدون صفحه', order=20)
        cls.industry = make_industry(slug='aviation', body='متن کامل صنعت')
        Service.objects.create(title='مشاوره', order=10)
        Advantage.objects.create(title='تخصص', order=10)
        Capability.objects.create(title='مهندسی', order=10)
        Certification.objects.create(title='ایمنی', order=10)
        Statistic.objects.create(value='10', label='سال', order=10)
        Testimonial.objects.create(quote='گزارش مثبت', author='مشتری', order=10)
        Milestone.objects.create(year='2020', title='آغاز', order=10)
        ProcessStep.objects.create(step_number=1, title='بررسی نیاز')
        FAQ.objects.create(question='چطور سفارش دهیم؟', answer='از فرم تماس', order=10)

    def test_home_is_company_first(self):
        """صفحه اصلی باید شرکت و فناوری‌ها را داشته باشد، نه فقط یک محصول."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        for key in ('technologies', 'industries', 'advantages', 'capabilities',
                    'product_lines', 'featured_products', 'statistics'):
            self.assertIn(key, response.context)
        self.assertTrue(response.context['technologies'])

    def test_home_works_with_no_products_at_all(self):
        """آزمون کلیدی: حذف همه‌ی محصولات نباید صفحه اصلی را خراب کند."""
        from products.models import Product
        Product.objects.all().delete()
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['featured_products']), [])

    def test_home_returns_404_without_company_record(self):
        CompanyInfo.objects.all().delete()
        self.assertEqual(self.client.get(reverse('core:home')).status_code, 404)

    def test_about_page_renders(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['milestones'])
        self.assertTrue(response.context['process_steps'])

    def test_technology_list_renders(self):
        response = self.client.get(reverse('core:technology_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/technology_list.html')
        self.assertEqual(len(response.context['technologies']), 2)

    def test_technology_detail_renders(self):
        response = self.client.get(self.tech.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/page_detail.html')
        self.assertEqual(response.context['kind'], 'technology')

    def test_inactive_technology_detail_returns_404(self):
        hidden = make_technology(slug='hidden-tech', title='پنهان', title_fa='پنهان', is_active=False)
        self.assertEqual(self.client.get(hidden.get_absolute_url()).status_code, 404)

    def test_industry_list_and_detail_render(self):
        self.assertEqual(self.client.get(reverse('core:industry_list')).status_code, 200)
        response = self.client.get(self.industry.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['kind'], 'industry')

    def test_quality_page_renders(self):
        response = self.client.get(reverse('core:quality'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/quality.html')
        self.assertTrue(response.context['capabilities'])

    def test_robots_txt_exposes_sitemap(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('Disallow: /admin/', body)
        self.assertIn('sitemap.xml', body)

    def test_sitemap_lists_pages_with_body_only(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('gas-systems', body)
        self.assertNotIn('no-page', body)


class LanguageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = make_company()
        make_technology(slug='gas-systems', body='متن')

    def test_home_available_in_both_languages(self):
        self.assertEqual(self.client.get('/fa/').status_code, 200)
        self.assertEqual(self.client.get('/en/').status_code, 200)

    def test_persian_is_rtl_and_english_is_ltr(self):
        self.assertIn('dir="rtl"', self.client.get('/fa/').content.decode())
        self.assertIn('dir="ltr"', self.client.get('/en/').content.decode())

    def test_translated_model_field_switches_with_language(self):
        self.assertIn('Atlas', self.client.get('/en/').content.decode())
        self.assertIn('Gas systems', self.client.get('/en/technologies/').content.decode())

    def test_language_switch_preserves_current_page(self):
        response = self.client.post(
            reverse('set_language'), {'language': 'en', 'next': '/en/technologies/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/en/technologies/')

    def test_context_processor_exposes_other_language_path(self):
        response = self.client.get('/fa/company/')
        self.assertEqual(response.context['other_language']['code'], 'en')
        self.assertEqual(response.context['other_language']['path'], '/en/company/')

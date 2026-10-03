"""
بارگذاری کامل محتوای کارفرما روی یک دیتابیس خالی — همان کاری که روی سرور
اصلی پس از استقرار انجام می‌شود — و بررسی این‌که هر بخش سایت با تصاویر و
متن‌ها بدون خطا رندر شود و اجرای دوباره چیزی را تکراری نکند.
"""

import shutil
import tempfile
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings

from products.models import Product, ProductDocument, ProductImage

from .models import (
    Certification, Client, CompanyInfo, Endorsement, GalleryImage, Service, ServiceImage,
)
from .tests import make_company

MEDIA_ROOT = tempfile.mkdtemp(prefix='atlas-test-client-')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ClientContentLoaderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        make_company()
        call_command('load_client_content', stdout=StringIO())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def counts(self):
        return {
            model.__name__: model.objects.count()
            for model in (Product, ProductImage, ProductDocument, Service, ServiceImage,
                          Certification, Client, Endorsement, GalleryImage)
        }

    def test_every_section_receives_its_images(self):
        company = CompanyInfo.objects.get()
        for field in ('hero_image', 'intro_image', 'trust_image', 'values_image', 'slogan_image',
                      'mission_image', 'vision_image', 'about_image', 'products_image', 'logo'):
            self.assertTrue(getattr(company, field), field)
        self.assertTrue(company.slogan_en)
        self.assertFalse(Product.objects.active().filter(image='').exists(), 'هر محصول عکس دارد')
        self.assertFalse(Service.objects.active().filter(image='').exists(), 'هر خدمت عکس دارد')
        self.assertEqual(Client.objects.active().count(), 11)
        self.assertEqual(Endorsement.objects.active().count(), 9)
        self.assertEqual(Certification.objects.active().count(), 5)

    def test_catalogue_data_reaches_products(self):
        buoys = Product.objects.get(slug='small-medium-buoys')
        self.assertEqual(buoys.model_code, 'AT-SB1 ~ AT-SB6')
        self.assertTrue(buoys.specs.filter(group_en='AT-SB6').exists())
        self.assertTrue(Product.objects.get(slug='shackles').specs.filter(is_highlight=True).exists())
        # هر کاتالوگ PDF فقط یک بار ذخیره شده و بین محصولات مشترک است.
        self.assertEqual(len(set(ProductDocument.objects.values_list('file', flat=True))), 3)

    def test_second_run_changes_nothing(self):
        before = self.counts()
        call_command('load_client_content', stdout=StringIO())
        self.assertEqual(self.counts(), before)

    def test_pages_render_in_both_languages(self):
        paths = ['/', '/company/', '/quality/', '/technologies/', '/products/',
                 '/products/small-medium-buoys/', '/products/shackles/',
                 '/products/?line=buoyancy-modules']
        for lang in ('fa', 'en'):
            for path in paths:
                response = self.client.get(f'/{lang}{path}')
                self.assertEqual(response.status_code, 200, f'/{lang}{path}')
        home = self.client.get('/fa/')
        self.assertContains(home, 'class="trust"')
        self.assertContains(home, 'class="slogan"')
        self.assertContains(home, 'clients__track')
        about = self.client.get('/en/company/')
        self.assertContains(about, 'data-lightbox="endorsements"')
        self.assertContains(about, 'Letters of satisfaction')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class FreshServerBootstrapTests(TestCase):
    """سرور تازه: دیتابیس کاملاً خالی، بدون هیچ رکورد «اطلاعات شرکت»."""

    def test_loader_builds_the_whole_site_from_an_empty_database(self):
        self.assertFalse(CompanyInfo.objects.exists())
        call_command('load_client_content', stdout=StringIO())
        company = CompanyInfo.objects.get()
        self.assertEqual(company.email, 'info@atlas-aim.com')
        self.assertEqual(company.name_en, 'Atlas Industrial Management')
        for lang in ('fa', 'en'):
            for path in ('/', '/company/', '/products/', '/contact/'):
                self.assertEqual(self.client.get(f'/{lang}{path}').status_code, 200, f'/{lang}{path}')

    def test_if_empty_runs_once_and_never_overwrites_admin_edits(self):
        call_command('load_client_content', '--if-empty', stdout=StringIO())
        company = CompanyInfo.objects.get()
        company.phone = '021-00000000'           # ویرایش مدیر سایت از پنل
        company.save()
        out = StringIO()
        call_command('load_client_content', '--if-empty', stdout=out)
        self.assertIn('--if-empty', out.getvalue())
        self.assertEqual(CompanyInfo.objects.get().phone, '021-00000000')

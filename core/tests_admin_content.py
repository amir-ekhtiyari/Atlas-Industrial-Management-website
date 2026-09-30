"""
مدیریت محتوای تیم و محصولات فقط از پنل مدیریت.

این تست‌ها فرم‌های واقعی پنل مدیریت را (با همان inline ها و فیلدهای ترجمه)
پر و ارسال می‌کنند و بعد صفحه‌های عمومی سایت را به هر دو زبان باز می‌کنند:
افزودن با عکس، خالی گذاشتن فیلدهای اختیاری، حذف عکس و حذف رکورد نباید
هیچ صفحه‌ای را خراب کند.
"""

import shutil
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from products.models import Product
from team.models import TeamMember

from .tests import make_company

MEDIA_ROOT = tempfile.mkdtemp(prefix='atlas-test-media-')


def png_upload(name='photo.png'):
    buffer = BytesIO()
    Image.new('RGB', (40, 40), (67, 75, 158)).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


def admin_form_data(response):
    """داده‌ی اولیه‌ی فرم پنل مدیریت، به‌همراه management form همه‌ی inline ها."""
    data = {}
    form = response.context['adminform'].form
    for name, field in form.fields.items():
        value = form[name].value()
        # فایل موجود را مرورگر دوباره ارسال نمی‌کند؛ فقط فایل تازه یا تیک «پاک کردن».
        if value is None or isinstance(field, forms.FileField) or hasattr(field, 'queryset') and not value:
            continue
        if isinstance(value, bool):
            if value:
                data[name] = 'on'
            continue
        data[name] = value
    for inline in response.context['inline_admin_formsets']:
        management = inline.formset.management_form
        for name in management.fields:
            data[management.add_prefix(name)] = management[name].value()
        for sub in inline.formset.forms:
            for name, field in sub.fields.items():
                value = sub[name].value()
                # مثل مرورگر: مقدار اولیه‌ی ردیف‌های خالی (مثلاً order=0) هم ارسال می‌شود.
                if value is None or value == '' or value is False or isinstance(field, forms.FileField):
                    continue
                data[sub.add_prefix(name)] = 'on' if value is True else value
    return data


def form_errors(response):
    """همه‌ی خطاهای فرم و inline ها، برای پیام شکست تست."""
    if response.status_code == 302 or not response.context:
        return ''
    ctx = response.context
    out = [str(ctx['adminform'].form.errors)]
    for inline in ctx.get('inline_admin_formsets', []):
        out.append(f'{inline.formset.prefix}: {inline.formset.errors} {inline.formset.non_form_errors()}')
    return ' | '.join(out)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class AdminContentFlexibilityTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        make_company()
        user = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'pass')
        self.client.force_login(user)

    def assert_pages_render(self, *url_names_and_kwargs):
        for lang in ('fa', 'en'):
            for name, kwargs in url_names_and_kwargs:
                url = f'/{lang}' + reverse(name, kwargs=kwargs)[3:]
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, url)

    # ── تیم ──────────────────────────────────────────────────────────
    def test_team_member_add_edit_clear_and_delete(self):
        add_url = reverse('admin:team_teammember_add')
        data = admin_form_data(self.client.get(add_url))
        data.update({'full_name_fa': 'مریم رضایی', 'photo': png_upload()})
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 302, form_errors(response))

        member = TeamMember.objects.get(full_name_fa='مریم رضایی')
        self.assertTrue(member.photo, 'عکس باید از پنل آپلود شود')
        self.assertEqual(member.position, '')
        self.assert_pages_render(('team:list', None), ('core:about', None))

        # پاک کردن عکس و همه‌ی فیلدهای اختیاری
        change_url = reverse('admin:team_teammember_change', args=[member.pk])
        data = admin_form_data(self.client.get(change_url))
        data.update({'photo-clear': 'on', 'bio_fa': '', 'bio_en': '', 'email': '', 'linkedin_url': ''})
        response = self.client.post(change_url, data)
        self.assertEqual(response.status_code, 302, form_errors(response))
        member.refresh_from_db()
        self.assertFalse(member.photo)
        page = self.client.get('/fa' + reverse('team:list')[3:])
        self.assertContains(page, 't-card__photo--blank')
        self.assertNotContains(page, 't-card__role')

        # حذف
        response = self.client.post(reverse('admin:team_teammember_delete', args=[member.pk]), {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TeamMember.objects.filter(pk=member.pk).exists())
        self.assert_pages_render(('team:list', None), ('core:about', None))

    # ── محصولات ──────────────────────────────────────────────────────
    def test_product_add_with_only_a_name_then_clear_and_delete(self):
        add_url = reverse('admin:products_product_add')
        data = admin_form_data(self.client.get(add_url))
        data.update({'name_fa': 'قلاب ایمنی', 'image': png_upload('p.png'), 'is_active': 'on'})
        response = self.client.post(add_url, data)
        self.assertEqual(response.status_code, 302, form_errors(response))

        product = Product.objects.get(name_fa='قلاب ایمنی')
        self.assertTrue(product.slug, 'نامک باید خودکار ساخته شود')
        self.assertTrue(product.image)
        detail = ('products:detail', {'slug': product.slug})
        self.assert_pages_render(('products:list', None), detail, ('core:home', None))

        # محصول هم‌نام دوم: نامک یکتا می‌ماند
        data = admin_form_data(self.client.get(add_url))
        data.update({'name_fa': 'قلاب ایمنی', 'is_active': 'on'})
        self.assertEqual(self.client.post(add_url, data).status_code, 302)
        twin = Product.objects.exclude(pk=product.pk).get(name_fa='قلاب ایمنی')
        self.assertNotEqual(twin.slug, product.slug)

        # حذف عکس
        change_url = reverse('admin:products_product_change', args=[product.pk])
        data = admin_form_data(self.client.get(change_url))
        data['image-clear'] = 'on'
        self.assertEqual(self.client.post(change_url, data).status_code, 302)
        product.refresh_from_db()
        self.assertFalse(product.image)
        self.assert_pages_render(('products:list', None), detail)
        self.assertContains(self.client.get('/fa' + reverse(*detail[:1], kwargs=detail[1])[3:]), 'p-card__blank')

        # حذف رکورد
        response = self.client.post(reverse('admin:products_product_delete', args=[product.pk]), {'post': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.get('/fa' + reverse(*detail[:1], kwargs=detail[1])[3:]).status_code, 404)
        self.assert_pages_render(('products:list', None), ('core:home', None))

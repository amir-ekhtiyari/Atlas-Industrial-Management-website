"""
اصلاحات متنی درخواستی کارفرما (مهر ۱۴۰۵) روی محتوای ذخیره‌شده در دیتابیس.

* «مونتاژ مجموعه‌های مکانیکی-الکتریکی» ← «مونتاژ مجموعه‌های مکانیکی»
* خدمت «مدیریت پروژه‌های فراساحل»: «مشارکت در پروژه‌های نصب سنگین و خط لوله»
* حوزه‌های کاری: «نفت و گاز و فراساحل»، «نصب سنگین»، «خدمات بازرگانی»
  (خدمات بازرگانی به‌جای فهرست «محصولات مرتبط»، توضیح خدمات را نشان می‌دهد)

همان تغییرات در load_client_content هم اعمال شده تا اجرای دوباره‌ی آن، این
متن‌ها را برنگرداند.
"""

from django.db import migrations

FA_REPL = [('مکانیکی-الکتریکی', 'مکانیکی'), ('مکانیکی–الکتریکی', 'مکانیکی')]
EN_REPL = [
    ('Mechanical–electrical', 'Mechanical'), ('mechanical–electrical', 'mechanical'),
    ('Mechanical-electrical', 'Mechanical'), ('mechanical-electrical', 'mechanical'),
]

INDUSTRY_TITLES = {
    'offshore-oil-gas': ('نفت و گاز و فراساحل', 'Oil, gas and offshore'),
    'heavy-lift-pipeline': ('نصب سنگین', 'Heavy installation'),
    'marine-shipping': ('خدمات بازرگانی', 'Commercial services'),
}
COMMERCIAL_DESC = (
    'خدمات گمرکی، حمل بین‌المللی، تأمین کالا از منابع خارجی و تحویل در داخل کشور.',
    'Customs services, international shipping, sourcing goods from foreign suppliers '
    'and delivery within Iran.',
)


def _replace(obj, fields):
    changed = False
    for field in fields:
        repl = EN_REPL if field.endswith('_en') else FA_REPL
        value = getattr(obj, field, None)
        if not value:
            continue
        new = value
        for old, rep in repl:
            new = new.replace(old, rep)
        if new != value:
            setattr(obj, field, new)
            changed = True
    return changed


def forwards(apps, schema_editor):
    Technology = apps.get_model('core', 'Technology')
    Capability = apps.get_model('core', 'Capability')
    Industry = apps.get_model('core', 'Industry')
    Service = apps.get_model('core', 'Service')

    text_fields = ['title', 'title_fa', 'title_en', 'description', 'description_fa',
                   'description_en']
    page_fields = text_fields + ['body', 'body_fa', 'body_en', 'meta_description',
                                 'meta_description_fa', 'meta_description_en']

    for obj in Technology.objects.all():
        if _replace(obj, page_fields):
            obj.save()
    for obj in Capability.objects.all():
        if _replace(obj, text_fields):
            obj.save()
    for obj in Industry.objects.all():
        if _replace(obj, page_fields):
            obj.save()

    for slug, (fa, en) in INDUSTRY_TITLES.items():
        obj = Industry.objects.filter(slug=slug).first()
        if not obj:
            continue
        obj.title = obj.title_fa = fa
        obj.title_en = en
        if slug == 'marine-shipping':
            obj.description = obj.description_fa = COMMERCIAL_DESC[0]
            obj.description_en = COMMERCIAL_DESC[1]
            obj.products.clear()
        obj.save()

    for obj in Service.objects.filter(title_fa='مدیریت پروژه‌های فراساحل'):
        fa = obj.description_fa or ''
        if 'مشارکت در پروژه‌های نصب سنگین' not in fa:
            fa = fa.replace('پروژه‌های نصب سنگین و خط لوله', 'مشارکت در پروژه‌های نصب سنگین و خط لوله')
            obj.description = obj.description_fa = fa
        en = obj.description_en or ''
        if 'participation in' not in en:
            obj.description_en = en.replace('heavy lift and pipeline projects',
                                            'participation in heavy lift and pipeline projects')
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_companyinfo_economic_code_companyinfo_national_id_and_more'),
        ('products', '0007_alter_product_description_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]

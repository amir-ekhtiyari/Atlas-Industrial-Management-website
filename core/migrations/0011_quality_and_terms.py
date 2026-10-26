"""
اصلاحات متنی کارفرما (مهر ۱۴۰۵، دور دوم):

* «عملکرد آزموده» به انتهای جمله‌ی توضیح سایت منتقل شد.
* عنوان انگلیسی «هدف بنیادین»: Core purpose.
* توضیح حوزه‌های کاری کامل‌تر شد.

همین متن‌ها در load_client_content هم به‌روز شده‌اند.
"""

from django.db import migrations

META = {
    'fa': (
        'عملکرد آزموده، تأمین مطمئن — راهکارهای صنعتی از نیاز تا تحویل، با تمرکز بر کیفیت و اطمینان.',
        'تأمین مطمئن و راهکارهای صنعتی از نیاز تا تحویل، با تمرکز بر کیفیت، اطمینان و عملکرد آزموده.',
    ),
    'en': (
        'Proven performance, reliable supply — industrial solutions from requirement to delivery, '
        'focused on quality and reliability.',
        'Reliable supply and industrial solutions from requirement to delivery, focused on '
        'quality, reliability and proven performance.',
    ),
}

# نامک: (جمله‌ی افزوده‌ی فا، جمله‌ی افزوده‌ی en)
INDUSTRY_EXTRA = {
    'offshore-oil-gas': (
        'تجهیزات این حوزه برای مقاومت در برابر خوردگی، رطوبت و بار سنگین انتخاب و آزموده '
        'می‌شوند و تحویل تا روی شناور یا سکو هماهنگ می‌شود.',
        'Equipment for this field is selected and tested to withstand corrosion, moisture and '
        'heavy loads, and delivery is coordinated right onto the vessel or platform.',
    ),
    'marine-shipping': (
        'از معرفی Consignee در کشورهای ثالث تا ترخیص در ایران و امارات، مسیر کالا را یک‌جا '
        'مدیریت می‌کنیم تا سفارش سالم و به‌موقع به دست شما برسد.',
        'From arranging consignees in third countries to clearance in Iran and the UAE, we '
        'manage the whole route so your order arrives intact and on time.',
    ),
    'process-manufacturing': (
        'از ساخت قطعه بر اساس نقشه یا نمونه تا تأمین قطعات یدکی خارجی، تلاش می‌کنیم زمان '
        'توقف خط به حداقل برسد.',
        'From making parts to a drawing or sample to sourcing imported spares, we work to keep '
        'line stoppages to a minimum.',
    ),
    'heavy-lift-pipeline': (
        'تجهیزات بالابری بر اساس استانداردهای مرجع انتخاب و همراه با مدارک آزمون تحویل '
        'می‌شوند.',
        'Lifting gear is selected to the reference standards and delivered with its test '
        'documentation.',
    ),
}


def forwards(apps, schema_editor):
    CompanyInfo = apps.get_model('core', 'CompanyInfo')
    Industry = apps.get_model('core', 'Industry')

    for company in CompanyInfo.objects.all():
        changed = False
        for lang, (old, new) in META.items():
            field = f'meta_description_{lang}'
            value = (getattr(company, field) or '').strip()
            if value == old:
                setattr(company, field, new)
                if lang == 'fa':
                    company.meta_description = new
                changed = True
        if (company.intro_title_en or '').strip() == 'Our purpose':
            company.intro_title_en = 'Core purpose'
            changed = True
        if changed:
            company.save()

    for slug, (fa, en) in INDUSTRY_EXTRA.items():
        obj = Industry.objects.filter(slug=slug).first()
        if not obj:
            continue
        if fa not in (obj.description_fa or ''):
            obj.description_fa = f'{(obj.description_fa or "").strip()} {fa}'.strip()
            obj.description = obj.description_fa
        if en not in (obj.description_en or ''):
            obj.description_en = f'{(obj.description_en or "").strip()} {en}'.strip()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_client_text_updates'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]

"""
اصلاح متنی کارفرما (آبان ۱۴۰۵): در متن فارسی به‌جای واژه‌ی «Consignee» معادل
فارسی آن، «گیرنده کالا»، نوشته می‌شود (حوزه‌ی خدمات بازرگانی، خدمات و معرفی شرکت).

فقط فیلدهای متنی فارسی (و فیلد پایه که همان فارسی است) عوض می‌شوند؛ متن انگلیسی
(*_en) دست نمی‌خورد. همین تغییر در load_client_content هم اعمال شده است.
"""

from django.db import migrations, models

OLD = 'Consignee'
NEW = 'گیرنده کالا'


def forwards(apps, schema_editor):
    for model in apps.get_app_config('core').get_models():
        fields = [
            f.name for f in model._meta.get_fields()
            if isinstance(f, (models.CharField, models.TextField)) and not f.name.endswith('_en')
        ]
        if not fields:
            continue
        for obj in model.objects.all():
            changed = []
            for name in fields:
                value = getattr(obj, name, None)
                if value and OLD in value:
                    setattr(obj, name, value.replace(OLD, NEW))
                    changed.append(name)
            if changed:
                obj.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_quality_and_terms'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]

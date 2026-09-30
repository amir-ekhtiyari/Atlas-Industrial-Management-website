"""
بارگذاری تصاویر و فایل‌های کارفرما در بخش‌های مختلف سایت.

منبع: پوشه‌ی `content/client/` در مخزن (نسخه‌ی بهینه‌شده‌ی فایل‌های 1.rar و 2.rar).
هر پوشه‌ی کارفرما به بخش هم‌نام خود در سایت رفته است؛ پوشه‌های بدون عکس
(صفحه‌ی اصلی، نوار اعتماد، شعار) از پوشه‌ی PUBLIC تصویر گرفته‌اند.

دستور idempotent است: فایلی که قبلاً نشسته دوباره کپی نمی‌شود و رکوردهایی
که از پنل مدیریت اضافه شده‌اند دست‌نخورده می‌مانند.

    python manage.py load_client_media
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import translation

from core.models import (
    Certification, Client, CompanyInfo, Endorsement, GalleryImage, Service, ServiceImage,
)
from products.models import Product, ProductDocument, ProductImage

from ._client_catalogue import PRODUCT_DETAILS

CONTENT = Path(settings.BASE_DIR) / 'content' / 'client'
STATIC = Path(settings.BASE_DIR) / 'static'

COMPANY_IMAGES = {
    'hero_image': 'company/hero.jpg',              # PUBLIC (پوشه‌ی Hero خالی بود)
    'trust_image': 'company/trust.jpg',            # PUBLIC (پوشه‌ی نوار اعتماد خالی بود)
    'slogan_image': 'company/slogan.jpg',          # PUBLIC (پوشه‌ی شعار خالی بود)
    'intro_image': 'company/purpose.jpg',          # هدف بنیادین
    'values_image': 'company/values.jpg',          # ارزش‌های بنیادین
    'mission_image': 'company/mission.jpg',        # مأموریت
    'vision_image': 'company/vision.jpg',          # چشم‌انداز
    'about_image': 'company/about-team.jpg',       # درباره ما
    'products_image': 'company/products-header.jpg',
    'og_image': 'company/hero.jpg',
}

# (فایل، توضیح فا، توضیح en) — مسیر با «static:» یعنی از تصاویر قبلی سایت
GALLERY = [
    ('static:images/about/atlas-workshop.jpg', 'کارگاه ساخت شناورسازهای اطلس', 'The Atlas buoyancy module workshop'),
    ('gallery/exhibition-booth.jpg', 'غرفه‌ی اطلس در نمایشگاه صنعت دریایی', 'The Atlas booth at a maritime exhibition'),
    ('static:images/about/offshore-platforms.jpg', 'سکوهای نفتی فراساحل', 'Offshore oil platforms'),
    ('static:images/about/heavy-lift-module.jpg', 'نصب ماژول سنگین در دریا', 'Heavy module installation at sea'),
    ('gallery/exhibition-visit.jpg', 'بازدید از غرفه‌ی اطلس', 'Visitors at the Atlas booth'),
    ('gallery/exhibition-team.jpg', 'تیم اطلس در نمایشگاه', 'The Atlas team at an exhibition'),
]

# (عنوان فا، عنوان en، صادرکننده فا، صادرکننده en، توضیح فا، توضیح en، فایل)
CERTIFICATIONS = [
    ('ISO 9001:2008', 'ISO 9001:2008', 'TÜV UK / CONAIPP', 'TÜV UK / CONAIPP',
     'سیستم مدیریت کیفیت — صادره ۲۰۱۳؛ دامنه: تأمین کالا، خدمات بازرگانی و مدیریت پروژه‌های فراساحل.',
     'Quality management system — issued 2013; scope: material supply, commercial services and offshore project management.',
     'certs/iso-9001.jpg'),
    ('ISO 14001:2004', 'ISO 14001:2004', 'TÜV UK / CONAIPP', 'TÜV UK / CONAIPP',
     'سیستم مدیریت زیست‌محیطی — صادره ۲۰۱۳.',
     'Environmental management system — issued 2013.',
     'certs/iso-14001.jpg'),
    ('OHSAS 18001:2007', 'OHSAS 18001:2007', 'TÜV UK / CONAIPP', 'TÜV UK / CONAIPP',
     'سیستم مدیریت ایمنی و بهداشت شغلی — صادره ۲۰۱۳.',
     'Occupational health and safety management system — issued 2013.',
     'certs/ohsas-18001.jpg'),
    ('عضویت انجمن مهندسی دریایی ایران', 'Member, Iranian Association of Naval Architecture & Marine Engineering',
     'انجمن مهندسی دریایی ایران', 'Iranian Association of Naval Architecture & Marine Engineering',
     'گواهی عضویت حقوقی شماره‌ی ۳۴۴ — صادره شهریور ۱۳۹۴.',
     'Corporate membership certificate No. 344 — issued September 2015.',
     'certs/iranian-marine-engineering.jpg'),
    ('تقدیرنامه‌ی نمایشگاه IRAN IMEX 2014', 'IRAN IMEX 2014 letter of appreciation',
     'سازمان بنادر و دریانوردی', 'Ports & Maritime Organization',
     'تقدیر از مشارکت در دومین نمایشگاه بین‌المللی دریایی ایران.',
     'Appreciation for taking part in the 2nd Iran International Maritime Exhibition.',
     'certs/iran-imex-2014.jpg'),
]

# (صادرکننده فا، صادرکننده en، فایل)
ENDORSEMENTS = [
    ('شرکت خدمات چاه‌های نفت پتروپارس (POSCO)', 'Petropars Oilfield Services (POSCO)', 'endorsements/posco.jpg'),
    ('پژوهشگاه صنعت نفت', 'Research Institute of Petroleum Industry', 'endorsements/ripi.jpg'),
    ('فناوری فراساحلی دلتا', 'Delta Offshore Technology', 'endorsements/delta-offshore.jpg'),
    ('فراساحلی امگا کیش', 'Omega Kish Offshore', 'endorsements/omega-kish-offshore.jpg'),
    ('خدمات مهندسی نفت کیش (KPE)', 'Kish Petroleum Engineering (KPE)', 'endorsements/kish-petroleum-engineering.jpg'),
    ('فناوری آب‌های عمیق', 'Deep Water Technology', 'endorsements/deep-water-technology.jpg'),
    ('توربین گازی خاورمیانه', 'Middle East Gas Turbine', 'endorsements/middle-east-gas-turbine.jpg'),
    ('طرقه انرژی', 'Torghe Energy', 'endorsements/torghe-energy.jpg'),
    ('شرکت بین‌المللی پترو براسان (PBI)', 'Petro Barasun International (PBI)', 'endorsements/petro-barasun.jpg'),
]

# (نام فا، نام en، فایل)
CLIENTS = [
    ('پتروپارس', 'Petropars', 'clients/petropars.png'),
    ('شرکت نفت فلات قاره ایران', 'Iranian Offshore Oil Company', 'clients/iooc.png'),
    ('مهندسی و ساخت تأسیسات دریایی ایران (IOEC)', 'Iranian Offshore Engineering & Construction (IOEC)', 'clients/ioec.png'),
    ('صدرا', 'SADRA', 'clients/sadra.png'),
    ('پژوهشگاه صنعت نفت', 'Research Institute of Petroleum Industry', 'clients/ripi.png'),
    ('شرکت حفاری شمال', 'North Drilling Company', 'clients/north-drilling.png'),
    ('پیمانکاری دریایی اوشنیک (OMC)', 'Oceanic Marine Contractors (OMC)', 'clients/oceanic-marine.png'),
    ('فناوری فراساحلی دلتا', 'Delta Offshore Technology', 'clients/delta-offshore.png'),
    ('فناوری آب‌های عمیق', 'Deep Offshore Technology', 'clients/deep-offshore-technology.png'),
    ('طرقه انرژی', 'Torghe Energy', 'clients/torghe-energy.png'),
    ('صبا نیرو', 'Saba Niroo', 'clients/saba-niroo.png'),
]

# عنوان فارسی خدمت ← [تصویر اصلی، تصاویر تکمیلی…]
SERVICE_IMAGES = {
    'خدمات بازرگانی (حمل‌ونقل و امور گمرکی)': ['commercial-1', 'commercial-2', 'commercial-3', 'commercial-4'],
    'مدیریت پروژه‌های فراساحل': ['offshore-1', 'offshore-2', 'offshore-3', 'offshore-4'],
    'مشاوره فنی انتخاب تجهیزات': ['technical-1', 'technical-2', 'technical-3', 'technical-4'],
    'خدمات پیش‌بینی وضع هوای دریایی': ['weather-1'],
}

# نامک محصول ← [تصویر اصلی، گالری…]
PRODUCT_IMAGES = {
    'shackles': ['shackles-1', 'shackles-2'],
    'hooks': ['hooks-1', 'hooks-2', 'hooks-3'],
    'blocks-sheaves': ['blocks-1', 'blocks-2'],
    'slings-grommets': ['slings-1', 'slings-2', 'slings-3', 'slings-4', 'slings-5'],
    'wire-rope': ['wire-rope-1', 'wire-rope-2', 'wire-rope-3'],
    'winches': ['winches-1'],
    'turnbuckles-swivels': ['turnbuckles-1', 'turnbuckles-2', 'turnbuckles-3'],
    'anchors': ['anchors-1'],
    'heavy-marine-equipment': ['heavy-marine-1', 'heavy-marine-2'],
    'hydraulic-mechanical-components': ['hydraulic-1', 'hydraulic-2', 'hydraulic-3', 'hydraulic-4'],
    'marine-platform-spare-parts': ['spare-parts-1', 'spare-parts-2', 'spare-parts-3', 'spare-parts-4'],
    'small-medium-buoys': ['buoys-small-1', 'buoys-small-2', 'buoys-small-3', 'buoys-small-4', 'buoys-small-5'],
    'mooring-buoys': ['buoys-mooring-1', 'buoys-mooring-2', 'buoys-mooring-3'],
    'pipeline-buoyancy-module': ['buoyancy-pipeline-1'],
    'bundle-buoyancy-module': ['buoyancy-bundle-1'],
}


def source(rel):
    path = STATIC / rel[len('static:'):] if rel.startswith('static:') else CONTENT / rel
    if not path.exists():
        raise CommandError(f'فایل منبع پیدا نشد: {path}')
    return path


def already(fieldfile, path):
    """آیا همین فایل (با هر پسوند یکتاسازی انبار) قبلاً در این فیلد نشسته است؟"""
    return bool(fieldfile) and Path(fieldfile.name).stem.startswith(path.stem)


def attach(fieldfile, path):
    """فایل را در فیلد می‌نشاند؛ اگر قبلاً نشسته باشد کاری نمی‌کند. خروجی: آیا تغییر کرد."""
    if already(fieldfile, path):
        return False
    with path.open('rb') as handle:
        fieldfile.save(path.name, File(handle), save=False)
    return True


def both(obj, field, fa, en):
    setattr(obj, field, fa)
    setattr(obj, f'{field}_fa', fa)
    setattr(obj, f'{field}_en', en)


class Command(BaseCommand):
    help = 'نشاندن تصاویر و فایل‌های کارفرما در بخش‌های سایت.'

    @transaction.atomic
    def handle(self, *args, **options):
        company = CompanyInfo.objects.first()
        if company is None:
            raise CommandError('رکورد «اطلاعات شرکت» وجود ندارد.')
        with translation.override(settings.LANGUAGE_CODE):
            self._company(company)
            self._ordered_images(GalleryImage, GALLERY, 'caption')
            self._certifications()
            self._named_images(Endorsement, ENDORSEMENTS, 'title', 'image')
            self._named_images(Client, CLIENTS, 'name', 'logo')
            self._services()
            self._products()
        self.stdout.write(self.style.SUCCESS('تصاویر و فایل‌های کارفرما نشانده شد.'))

    def _company(self, company):
        changed = [f for f, rel in COMPANY_IMAGES.items() if attach(getattr(company, f), source(rel))]
        if changed:
            company.save()
        self.stdout.write(f'  اطلاعات شرکت: {len(changed)} تصویر تازه')

    def _ordered_images(self, model, rows, text_field):
        created = 0
        for index, (rel, fa, en) in enumerate(rows, start=1):
            path = source(rel)
            obj = next((o for o in model.objects.all() if already(o.image, path)), None)
            if obj is None:
                obj = model(); attach(obj.image, path); created += 1
            both(obj, text_field, fa, en)
            obj.order, obj.is_active = index * 10, True
            obj.save()
        self.stdout.write(f'  {model._meta.verbose_name_plural}: {len(rows)} مورد ({created} تازه)')

    def _named_images(self, model, rows, text_field, image_field):
        created = 0
        for index, (fa, en, rel) in enumerate(rows, start=1):
            obj = model.objects.filter(**{f'{text_field}_fa': fa}).first()
            if obj is None:
                obj = model(); created += 1
            both(obj, text_field, fa, en)
            attach(getattr(obj, image_field), source(rel))
            obj.order, obj.is_active = index * 10, True
            obj.save()
        self.stdout.write(f'  {model._meta.verbose_name_plural}: {len(rows)} مورد ({created} تازه)')

    def _certifications(self):
        for index, (t_fa, t_en, i_fa, i_en, d_fa, d_en, rel) in enumerate(CERTIFICATIONS, start=1):
            obj = Certification.objects.filter(title_fa=t_fa).first() or Certification(icon='icon-certificate')
            both(obj, 'title', t_fa, t_en)
            both(obj, 'issuer', i_fa, i_en)
            both(obj, 'description', d_fa, d_en)
            attach(obj.image, source(rel))
            obj.order, obj.is_active = index * 10, True
            obj.save()
        self.stdout.write(f'  استانداردها و گواهی‌نامه‌ها: {len(CERTIFICATIONS)} مورد')

    def _services(self):
        for title_fa, names in SERVICE_IMAGES.items():
            service = Service.objects.filter(title_fa=title_fa).first()
            if service is None:
                raise CommandError(f'خدمت «{title_fa}» پیدا نشد؛ ابتدا load_client_content را اجرا کنید.')
            paths = [CONTENT / 'services' / f'{n}.jpg' for n in names]
            if attach(service.image, paths[0]):
                service.save()
            self._gallery(ServiceImage, {'service': service}, paths[1:])
        self.stdout.write(f'  خدمات: تصاویر {len(SERVICE_IMAGES)} خدمت')

    def _gallery(self, model, parent, paths):
        existing = list(model.objects.filter(**parent))
        for index, path in enumerate(paths, start=1):
            obj = next((o for o in existing if already(o.image, path)), None)
            if obj is None:
                obj = model(**parent); attach(obj.image, path)
            obj.order = index * 10
            obj.save()

    def _products(self):
        # هر کاتالوگ PDF یک بار در انبار ذخیره می‌شود و همه‌ی محصولات به همان فایل اشاره می‌کنند.
        shared_files = {}
        for slug, names in PRODUCT_IMAGES.items():
            product = Product.objects.filter(slug=slug).first()
            if product is None:
                raise CommandError(f'محصول «{slug}» پیدا نشد؛ ابتدا load_client_content را اجرا کنید.')
            paths = [CONTENT / 'products' / f'{n}.jpg' for n in names]
            if attach(product.image, paths[0]):
                product.save()
            self._gallery(ProductImage, {'product': product}, paths[1:])

            for index, (t_fa, t_en, rel) in enumerate(PRODUCT_DETAILS.get(slug, {}).get('docs', []), start=1):
                doc = ProductDocument.objects.filter(product=product, title_fa=t_fa).first()
                if doc is None:
                    doc = ProductDocument(product=product)
                both(doc, 'title', t_fa, t_en)
                path = source(rel)
                if path in shared_files:
                    doc.file.name = shared_files[path]
                else:
                    attach(doc.file, path)
                    shared_files[path] = doc.file.name
                doc.order = index * 10
                doc.save()
        self.stdout.write(f'  محصولات: تصاویر و مدارک {len(PRODUCT_IMAGES)} محصول')

"""
بارگذاری محتوای نهایی کارفرما (شرکت مدیریت صنعتی اطلس) در دیتابیس.

منبع متن‌ها:
* «نسخه فاینال نهایی.docx» — هدف بنیادین، چشم‌انداز، مأموریت، ارزش‌ها،
  درباره ما، متن Hero و نوار اعتماد. متن فارسی عیناً آمده؛ فقط غلط‌های
  املایی و نیم‌فاصله‌ها اصلاح شده است.
* «محصولات و خدمات.docx» — خطوط محصول، اقلام و خدمات.
* بخش‌هایی که کارفرما متنی برایشان نداده بود (حوزه‌های فعالیت، صنعت‌ها،
  توانمندی‌ها، فرایند، پرسش‌های متداول، بازار جهانی، فراخوان) بر پایه‌ی
  همان دو سند نوشته شده‌اند.

دستور idempotent است و بارها قابل اجراست (روی سرور اصلی هم):

    python manage.py load_client_content

رکوردهای محتوای آزمایشی قبلی حذف نمی‌شوند؛ فقط «نمایش در سایت» آن‌ها
خاموش می‌شود تا از پنل مدیریت قابل بازگشت باشند. به همین دلیل اجرای
دوباره‌ی seed_site_content هم آن‌ها را دوباره نمی‌سازد.
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import translation

from core.models import (
    Advantage,
    Capability,
    CompanyInfo,
    FAQ,
    Industry,
    ProcessStep,
    Service,
    Statistic,
    Technology,
)
from products.models import Category, Product

# ─────────────────────────────────────────────── اطلاعات شرکت
# فیلد: (فا، en)

COMPANY = {
    'name': (
        'شرکت مدیریت صنعتی اطلس',
        'Atlas Industrial Management',
    ),
    'hero_title': (
        'تأمین و تولید صنعتی، با عملکرد و کیفیت قابل اثبات',
        'Industrial supply and manufacturing, with proven performance and quality',
    ),
    'hero_text': (
        'از شناسایی نیاز و انتخاب مسیر تأمین تا تولید، کنترل کیفیت و تحویل نهایی، '
        'در کنار پروژه‌های صنعتی شما هستیم؛ با تمرکز بر کیفیت، سرعت، مستندسازی و '
        'اطمینان در اجرا.',
        'From identifying the need and choosing the right supply route to manufacturing, '
        'quality control and final delivery, we stand beside your industrial projects — '
        'with a focus on quality, speed, documentation and dependable execution.',
    ),
    'intro_title': (
        'هدف بنیادین',
        'Our purpose',
    ),
    'intro_text': (
        'در صنایعی که خطا، تأخیر یا نقص محصول هزینه‌ساز است، ما فقط کالا تحویل '
        'نمی‌دهیم؛ تلاش می‌کنیم بخشی قابل اتکا از زنجیره تأمین و عملکرد مشتری باشیم.\n\n'
        'از انتخاب و تأمین تا تولید، کنترل کیفیت، مونتاژ و تحویل، هدف ما این است که '
        'مشتری بتواند با اطمینان بیشتری روی کیفیت، زمان و عملکرد محصول حساب کند.',
        'In industries where an error, a delay or a defective product carries a real cost, '
        'we don’t just deliver goods — we work to be a dependable part of our customers’ '
        'supply chain and operations.\n\n'
        'From selection and sourcing through manufacturing, quality control, assembly and '
        'delivery, our aim is to let customers count on product quality, timing and '
        'performance with greater confidence.',
    ),
    'about_text': (
        'فعالیت ما با تمرکز بر نیازهای تخصصی صنایع در سال 1389 آغاز شد و در ادامه، با '
        'توجه به نیاز به تولید در داخل کشور توسط شرکت‌های دانش‌بنیان، با توسعه دانش فنی '
        'و شکل‌گیری توانمندی‌های تخصصی، دامنه فعالیت از تأمین صرف فراتر رفت.\n\n'
        'امروز، رویکرد ما ترکیبی از شناخت نیاز، تأمین، تولید و ارائه راهکارهای صنعتی '
        'است؛ رویکردی که به مشتری اجازه می‌دهد متناسب با هر پروژه، مسیر مناسب‌تری برای '
        'تأمین و اجرا داشته باشد.\n\n'
        'ما معتقدیم یک تأمین‌کننده یا سازنده موفق، فقط فروشنده کالا نیست؛ بخشی از '
        'زنجیره موفقیت پروژه مشتری است.\n\n'
        'به همین دلیل، تلاش می‌کنیم کیفیت، زمان و مستندات را در تمام زنجیره فعالیت خود '
        'به‌صورت هماهنگ مدیریت کنیم.',
        'We began in 2010 with a focus on the specialised needs of industry. As the need '
        'for domestic manufacturing by knowledge-based companies grew, we developed our '
        'technical know-how and specialist capabilities, and our work expanded beyond '
        'supply alone.\n\n'
        'Today our approach combines understanding the need, sourcing, manufacturing and '
        'industrial solutions — an approach that gives each customer a better-suited route '
        'to supply and execution for every project.\n\n'
        'We believe a successful supplier or manufacturer is more than a seller of goods: '
        'it is part of the chain that makes the customer’s project succeed.\n\n'
        'That is why we work to manage quality, timing and documentation together, across '
        'every link of our operations.',
    ),
    'mission_text': (
        'مأموریت ما ایجاد یک زنجیره تأمین و طراحی، تولید، مونتاژ و تضمین کیفیت قطعات '
        'فلزی و پلیمری و مجموعه‌های مکانیکی-الکتریکی مقاوم در برابر تمامی عوامل مخرب '
        'است؛ به‌گونه‌ای که مشتریان ما بتوانند خط تولید یا حوزه عملیاتی خود را بدون '
        'توقف، بدون بازخورد منفی و بدون بازگشت محصول اداره کنند و محصولات تحویل‌شده، '
        'عملکرد تست‌شده و مستند داشته باشد.\n\n'
        'ما اطلاعات درستی از نظر کیفیت، زمان و هزینه به مشتریان خود می‌دهیم تا '
        'تصمیم‌گیری شفاف‌تری داشته باشند.',
        'Our mission is to build a chain of supply, design, manufacturing, assembly and '
        'quality assurance for metal and polymer parts and mechanical–electrical assemblies '
        'that stand up to every damaging factor — so that our customers can run their '
        'production lines and operations without stoppages, without negative feedback and '
        'without returns, and every product delivered comes with tested, documented '
        'performance.\n\n'
        'We give our customers accurate information on quality, time and cost, so they can '
        'make clearer decisions.',
    ),
    'vision_text': (
        'تا افق ۱۴۲۰، به یکی از نام‌های معتبر و قابل اعتماد منطقه در تأمین، تولید و '
        'مجموعه‌سازی صنعتی تبدیل شویم؛ نامی که مشتریان و مهندسان صنایع هدف، در '
        'پروژه‌های حساس خود با اطمینان به آن رجوع می‌کنند.\n\n'
        'در یک کلام، جایی که خطاها گران است، ما می‌خواهیم اولین نامی باشیم که اعتماد '
        'حرفه‌ای را در ذهن مشتریان خود می‌سازیم.',
        'By 2041, to become one of the region’s most reputable and trusted names in '
        'industrial supply, manufacturing and assembly — a name that customers and engineers '
        'in our target industries turn to with confidence on their most critical '
        'projects.\n\n'
        'In a word: where mistakes are expensive, we want to be the first name that builds '
        'professional trust in our customers’ minds.',
    ),
    'global_title': (
        'تأمین و تحویل در مقیاس بین‌المللی',
        'Supply and delivery across borders',
    ),
    'global_text': (
        'زنجیره تأمین ما به مرزهای ایران محدود نیست. کالا را از تمام نقاط جهان به ایران '
        'و بالعکس حمل می‌کنیم، در کشورهای ثالث Consignee معرفی می‌کنیم و امور گمرکی در '
        'ایران و امارات متحده عربی را انجام می‌دهیم.\n\n'
        'برای پروژه‌های فراساحل، تحویل مستقیم کالا به شناور و محل پروژه را هماهنگ '
        'می‌کنیم تا تأمین در زمانی که پروژه به آن نیاز دارد کامل شود.',
        'Our supply chain doesn’t stop at Iran’s borders. We ship goods from anywhere in the '
        'world to Iran and from Iran worldwide, arrange consignees in third countries, and '
        'handle customs clearance in Iran and the United Arab Emirates.\n\n'
        'For offshore projects, we coordinate delivery straight to the vessel or project '
        'site, so supply is complete exactly when the project needs it.',
    ),
    'cta_title': (
        'درخواست مشاوره یا استعلام تأمین',
        'Request a consultation or supply quote',
    ),
    'cta_text': (
        'نیاز فنی، مشخصات و زمان‌بندی پروژه‌ی خود را برای ما بنویسید تا مسیر مناسب '
        'تأمین، ساخت و تحویل را با شما بررسی کنیم.',
        'Send us your technical requirement, specifications and project timeline, and we’ll '
        'work out the right route for supply, manufacturing and delivery with you.',
    ),
    'meta_description': (
        'عملکرد آزموده، تأمین مطمئن — راهکارهای صنعتی از نیاز تا تحویل، با تمرکز بر '
        'کیفیت و اطمینان.',
        'Proven performance, reliable supply — industrial solutions from requirement to '
        'delivery, focused on quality and reliability.',
    ),
}

# تصاویر شرکت: فیلد ← مسیر فایل در static
COMPANY_IMAGES = {
    'about_image': 'images/about/atlas-workshop.jpg',
    'logo': 'brand/atlas-logo.png',
}

# ─────────────────────────────────────────────── حوزه‌های فعالیت (مدل Technology)
# (نامک، عنوان فا، عنوان en، توضیح فا، توضیح en، متن صفحه فا، متن صفحه en، آیکون)

TECHNOLOGIES = [
    (
        'industrial-sourcing',
        'تأمین و بازرگانی صنعتی', 'Industrial sourcing and procurement',
        'شناسایی نیاز، انتخاب مسیر تأمین و خرید قطعات و تجهیزات صنعتی از منابع معتبر '
        'داخلی و خارجی.',
        'Identifying the requirement, choosing the supply route and procuring industrial '
        'parts and equipment from reliable domestic and international sources.',
        'تأمین برای ما از شناخت دقیق نیاز شروع می‌شود: مشخصات فنی، شرایط کاری، '
        'استانداردهای پروژه و محدودیت زمانی. بر همین پایه، مسیر مناسب تأمین — خرید، '
        'ساخت داخلی یا ترکیبی از هر دو — انتخاب می‌شود.\n\n'
        'هر قلم پیش از ارسال با مشخصات سفارش تطبیق داده می‌شود و مدارک آن همراه کالا '
        'تحویل می‌شود.',
        'For us, sourcing starts with a precise understanding of the requirement: technical '
        'specifications, operating conditions, project standards and time constraints. On '
        'that basis we choose the right supply route — purchase, domestic manufacture, or a '
        'combination of both.\n\n'
        'Every item is checked against the order specification before dispatch, and its '
        'documents are delivered with the goods.',
        'icon-route',
    ),
    (
        'metal-polymer-manufacturing',
        'ساخت قطعات فلزی و پلیمری', 'Metal and polymer part manufacturing',
        'ساخت قطعات فلزی و پلیمری مقاوم برای محیط‌های دریایی و صنعتی، بر اساس نقشه، '
        'نمونه یا مشخصات فنی مشتری.',
        'Durable metal and polymer parts for marine and industrial environments, made to '
        'the customer’s drawing, sample or technical specification.',
        'بخشی از نیاز صنایع هدف با تولید داخلی پاسخ داده می‌شود. ما قطعات فلزی و '
        'پلیمری را بر اساس نقشه، نمونه‌ی موجود یا مشخصات فنی مشتری می‌سازیم؛ با انتخاب '
        'مواد متناسب با شرایط کاری و عوامل مخرب محیطی مانند خوردگی، رطوبت و بار '
        'مکانیکی.\n\n'
        'کنترل ابعادی و کیفی در طول ساخت انجام می‌شود و سوابق آن در شناسنامه‌ی فنی قطعه '
        'ثبت می‌شود.',
        'Part of our target industries’ demand is met through domestic manufacturing. We '
        'make metal and polymer parts to the customer’s drawing, an existing sample or a '
        'technical specification, choosing materials to suit the operating conditions and '
        'environmental threats such as corrosion, moisture and mechanical load.\n\n'
        'Dimensional and quality checks are carried out during manufacture, and the records '
        'are kept in each part’s technical file.',
        'icon-factory',
    ),
    (
        'mechanical-electrical-assembly',
        'مونتاژ مجموعه‌های مکانیکی-الکتریکی', 'Mechanical–electrical assembly',
        'مونتاژ و مجموعه‌سازی قطعات در قالب مجموعه‌های مکانیکی-الکتریکی آماده‌ی نصب و '
        'بهره‌برداری.',
        'Assembling parts into mechanical–electrical assemblies that are ready to install '
        'and operate.',
        'بسیاری از پروژه‌ها به یک مجموعه‌ی کامل و آماده‌ی نصب نیاز دارند، نه قطعات جدا از '
        'هم. ما قطعات تأمین‌شده و ساخته‌شده را در قالب مجموعه‌های مکانیکی-الکتریکی '
        'مونتاژ می‌کنیم تا در محل پروژه با کمترین کار اضافه نصب شوند.\n\n'
        'عملکرد هر مجموعه پیش از تحویل آزموده می‌شود.',
        'Many projects need a complete, ready-to-install assembly rather than separate '
        'parts. We assemble sourced and manufactured parts into mechanical–electrical '
        'assemblies so they can be installed on site with minimal extra work.\n\n'
        'Every assembly is performance-tested before delivery.',
        'icon-cog',
    ),
    (
        'quality-control-testing',
        'کنترل کیفیت و آزمون عملکرد', 'Quality control and performance testing',
        'بازرسی، اندازه‌گیری و آزمون عملکرد پیش از تحویل، با ثبت نتایج در شناسنامه‌ی فنی '
        'هر محصول.',
        'Inspection, measurement and performance testing before delivery, with results '
        'recorded in each product’s technical file.',
        'تحویل محصول برای ما بر مبنای کنترل و شواهد قابل ارائه انجام می‌شود. بازرسی '
        'ورودی، کنترل ابعادی و آزمون عملکرد، بسته به نوع محصول و الزامات پروژه، پیش از '
        'تحویل انجام می‌شود.\n\n'
        'نتایج در شناسنامه‌ی فنی محصول ثبت و همراه مدارک در اختیار مشتری قرار می‌گیرد.',
        'We deliver on the basis of inspection and verifiable evidence. Incoming inspection, '
        'dimensional checks and performance testing are carried out before delivery, '
        'according to the product type and project requirements.\n\n'
        'Results are recorded in the product’s technical file and handed to the customer '
        'with the rest of the documentation.',
        'icon-flask',
    ),
    (
        'documentation-traceability',
        'مستندسازی و ردیابی‌پذیری', 'Documentation and traceability',
        'نگهداری سوابق تولید، تأمین و کنترل برای هر محصول؛ تا هر قلم تحویل‌شده قابل '
        'ردیابی باشد.',
        'Keeping production, sourcing and inspection records for every product, so each '
        'item delivered can be traced.',
        'برای هر محصول یک شناسنامه‌ی فنی نگهداری می‌شود: منبع تأمین یا سوابق تولید، '
        'نتایج کنترل و آزمون، و مدارک همراه.\n\n'
        'این سوابق در صورت نیاز به ارزیابی، تعویض یا سفارش مجدد، مبنای پاسخ‌گویی دقیق به '
        'مشتری است.',
        'Every product has a technical file: its supply source or production records, '
        'inspection and test results, and accompanying documents.\n\n'
        'When a product needs to be assessed, replaced or reordered, these records are the '
        'basis for giving the customer an accurate answer.',
        'icon-clipboard',
    ),
    (
        'logistics-offshore-delivery',
        'لجستیک و تحویل فراساحل', 'Logistics and offshore delivery',
        'حمل بین‌المللی، امور گمرکی و تحویل کالا به شناورها و پروژه‌های فراساحل.',
        'International shipping, customs clearance and delivery to vessels and offshore '
        'projects.',
        'تأمین تنها زمانی کامل است که کالا به‌موقع و سالم به محل پروژه برسد.\n\n'
        'ما حمل کالا بین ایران و سایر کشورها، امور گمرکی در ایران و امارات متحده عربی، و '
        'تحویل کالا به شناورها و پروژه‌های فراساحل را هماهنگ می‌کنیم.',
        'Supply is only complete when the goods reach the project site on time and '
        'intact.\n\n'
        'We coordinate shipping between Iran and other countries, customs clearance in Iran '
        'and the United Arab Emirates, and delivery to vessels and offshore projects.',
        'icon-globe',
    ),
]

# ─────────────────────────────────────────────── صنعت‌ها
# (نامک، عنوان فا، عنوان en، توضیح فا، توضیح en، آیکون)

INDUSTRIES = [
    (
        'offshore-oil-gas',
        'نفت و گاز فراساحل', 'Offshore oil and gas',
        'سکوها، شناورها و پروژه‌های فراساحلی که به تجهیزات مقاوم، قطعات یدکی و تحویل '
        'به‌موقع در محل نیاز دارند.',
        'Platforms, vessels and offshore projects that need robust equipment, spare parts '
        'and on-time delivery on site.',
        'icon-layers',
    ),
    (
        'marine-shipping',
        'دریانوردی و کشتیرانی', 'Marine and shipping',
        'تجهیزات، قطعات یدکی و اقلام ریگینگ برای شناورها، ناوگان دریایی و عملیات بندری.',
        'Equipment, spare parts and rigging for vessels, marine fleets and port operations.',
        'icon-route',
    ),
    (
        'process-manufacturing',
        'صنایع فرآیندی و تولیدی', 'Process and manufacturing industries',
        'قطعات فلزی و پلیمری، مجموعه‌های مکانیکی-الکتریکی و تأمین قطعات برای خطوط '
        'تولیدی که توقف در آن‌ها پرهزینه است.',
        'Metal and polymer parts, mechanical–electrical assemblies and component supply for '
        'production lines where downtime is costly.',
        'icon-factory',
    ),
    (
        'heavy-lift-pipeline',
        'پروژه‌های بالابری سنگین و خط لوله', 'Heavy lift and pipeline projects',
        'تجهیزات لیفتینگ و ریگینگ، مشاوره‌ی انتخاب تجهیزات و پشتیبانی پروژه‌های نصب '
        'سنگین و خط لوله.',
        'Lifting and rigging equipment, equipment-selection advice and support for heavy '
        'lift and pipeline projects.',
        'icon-weight',
    ),
]

# ─────────────────────────────────────────────── ارزش‌های بنیادین (مدل Advantage)
# (عنوان فا، عنوان en، توضیح فا، توضیح en، آیکون)

ADVANTAGES = [
    (
        'دقت وسواس‌گونه', 'Meticulous precision',
        'اندازه‌گیری، کنترل کیفیت و اجرای دقیق؛ با حساسیت نسبت به جزئیاتی که بر عملکرد '
        'محصول اثر می‌گذارند.',
        'Measurement, quality control and precise execution — with close attention to every '
        'detail that affects product performance.',
        'icon-target',
    ),
    (
        'صداقت فنی', 'Technical honesty',
        'گزارش وضعیت واقعی محصول و پروژه، حتی زمانی که نتیجه مطلوب نیست.',
        'Reporting the real status of the product and project, even when the result is not '
        'what we hoped for.',
        'icon-check-circle',
    ),
    (
        'ردیابی‌پذیری', 'Traceability',
        'حفظ شناسنامه فنی و سوابق تولید، تأمین، کنترل و مستندات.',
        'Keeping a technical file for every item, with its production, sourcing, inspection '
        'and documentation records.',
        'icon-clipboard',
    ),
    (
        'اثبات قبل از تحویل', 'Proof before delivery',
        'تحویل محصول بر مبنای کنترل و شواهد قابل ارائه، نه صرفاً ادعا.',
        'Products are delivered on the basis of inspection and verifiable evidence — not '
        'just claims.',
        'icon-certificate',
    ),
    (
        'احترام به صنعت مشتری', 'Respect for the customer’s industry',
        'شناخت نیازها، الزامات و حساسیت‌های صنعت و پروژه پیش از پیشنهاد راهکار.',
        'Understanding the needs, requirements and sensitivities of the industry and project '
        'before proposing a solution.',
        'icon-handshake',
    ),
    (
        'یادگیری از خطا', 'Learning from mistakes',
        'ثبت انحراف‌ها و استفاده از آن‌ها برای اصلاح فرآیند و جلوگیری از تکرار.',
        'Recording deviations and using them to improve our processes and prevent them from '
        'happening again.',
        'icon-chart',
    ),
]

# ─────────────────────────────────────────────── توانمندی‌ها
# (عنوان فا، عنوان en، توضیح فا، توضیح en، آیکون)

CAPABILITIES = [
    (
        'شناخت نیاز و مشاوره فنی', 'Needs analysis and technical advice',
        'بررسی مشخصات، شرایط کاری و استانداردهای پروژه پیش از پیشنهاد راهکار.',
        'Reviewing specifications, operating conditions and project standards before '
        'proposing a solution.',
        'icon-headset',
    ),
    (
        'تأمین از منابع معتبر', 'Sourcing from reliable suppliers',
        'انتخاب و خرید قطعات و تجهیزات از تأمین‌کنندگان داخلی و خارجی قابل اتکا.',
        'Selecting and purchasing parts and equipment from dependable domestic and '
        'international suppliers.',
        'icon-route',
    ),
    (
        'ساخت قطعه', 'Part manufacturing',
        'تولید قطعات فلزی و پلیمری بر اساس نقشه، نمونه یا مشخصات فنی.',
        'Producing metal and polymer parts to a drawing, sample or technical specification.',
        'icon-factory',
    ),
    (
        'مونتاژ و مجموعه‌سازی', 'Assembly',
        'مونتاژ مجموعه‌های مکانیکی-الکتریکی آماده‌ی نصب.',
        'Building ready-to-install mechanical–electrical assemblies.',
        'icon-cog',
    ),
    (
        'کنترل کیفیت و آزمون', 'Quality control and testing',
        'بازرسی و آزمون عملکرد پیش از تحویل، با ثبت نتایج.',
        'Inspection and performance testing before delivery, with recorded results.',
        'icon-flask',
    ),
    (
        'لجستیک و تحویل', 'Logistics and delivery',
        'حمل، امور گمرکی و تحویل به محل پروژه، از جمله شناورها و سکوهای فراساحل.',
        'Shipping, customs and delivery to the project site — including vessels and offshore '
        'platforms.',
        'icon-globe',
    ),
]

# ─────────────────────────────────────────────── خدمات
# (عنوان فا، عنوان en، توضیح فا، توضیح en، آیکون)

SERVICES = [
    (
        'خدمات بازرگانی (حمل‌ونقل و امور گمرکی)',
        'Commercial services — shipping and customs',
        'حمل کالا از تمام نقاط جهان به ایران و بالعکس؛ معرفی Consignee در کشورهای ثالث و '
        'ترانزیت به ایران؛ تحویل کالا به شناور و پروژه‌های فراساحل؛ خدمات گمرکی در ایران '
        'و امارات متحده عربی.',
        'Shipping goods from anywhere in the world to Iran and from Iran worldwide; arranging '
        'consignees in third countries and transit to Iran; delivery to vessels and offshore '
        'projects; customs services in Iran and the United Arab Emirates.',
        'icon-route',
    ),
    (
        'مدیریت پروژه‌های فراساحل',
        'Offshore project management',
        'نقشه‌برداری ژئوتکنیک و ژئوفیزیک (Geotechnical & Geophysical Survey)؛ مدیریت ناوگان '
        'و شناور (Fleet Management)؛ پروژه‌های نصب سنگین و خط لوله (Heavy Lift & Pipeline '
        'Projects).',
        'Geotechnical and geophysical surveys; fleet and vessel management; heavy lift and '
        'pipeline projects.',
        'icon-layers',
    ),
    (
        'مشاوره فنی انتخاب تجهیزات',
        'Technical consultation and equipment selection',
        'راهنمایی فنی تخصصی برای انتخاب صحیح تجهیزات لیفتینگ و ریگینگ بر اساس نوع بار، '
        'شرایط محیطی (دریایی/فراساحل) و استانداردهای ایمنی پروژه، کاهش ریسک خرید نادرست '
        'و افزایش عمر مفید تجهیزات.',
        'Specialist technical guidance on choosing the right lifting and rigging equipment '
        'for the type of load, the environment (marine/offshore) and the project’s safety '
        'standards — reducing the risk of a wrong purchase and extending equipment service '
        'life.',
        'icon-headset',
    ),
]

# ─────────────────────────────────────────────── نوار اعتماد (مدل Statistic)
# (مقدار، عنوان فا، عنوان en) — ترتیب مهم است: صفحه اصلی چهار مورد اول را نشان می‌دهد.

STATISTICS = [
    ('1389', 'سال تأسیس', 'Year founded (2010)'),
    ('62', 'تعداد محصولات', 'Products'),
    ('79', 'پروژه‌ها', 'Projects'),
    ('31', 'تعداد مشتریان صنعتی', 'Industrial clients'),
    ('79', 'مجموعه‌های تحویل‌شده', 'Assemblies delivered'),
]

# ─────────────────────────────────────────────── فرایند کار
# (شماره، عنوان فا، عنوان en، توضیح فا، توضیح en)

PROCESS = [
    (
        1, 'شناخت نیاز', 'Understanding the requirement',
        'مشخصات فنی، شرایط کاری، استانداردها و زمان‌بندی پروژه را با تیم شما بررسی '
        'می‌کنیم.',
        'We review the technical specifications, operating conditions, standards and '
        'project timeline with your team.',
    ),
    (
        2, 'انتخاب مسیر تأمین', 'Choosing the supply route',
        'بسته به نیاز، مسیر مناسب — تأمین، ساخت داخلی یا ترکیبی از هر دو — همراه با '
        'برآورد روشن زمان و هزینه پیشنهاد می‌شود.',
        'Depending on the need, we propose the right route — sourcing, domestic manufacture '
        'or a mix of both — with a clear estimate of time and cost.',
    ),
    (
        3, 'تولید، مونتاژ و کنترل کیفیت', 'Manufacturing, assembly and quality control',
        'قطعات تأمین یا ساخته می‌شوند، در صورت نیاز مونتاژ می‌شوند و پیش از تحویل کنترل '
        'و آزمون می‌شوند.',
        'Parts are sourced or manufactured, assembled where required, and inspected and '
        'tested before delivery.',
    ),
    (
        4, 'تحویل و مستندات', 'Delivery and documentation',
        'کالا همراه با مدارک و شناسنامه‌ی فنی، در محل پروژه یا روی شناور تحویل داده '
        'می‌شود.',
        'Goods are delivered with their documents and technical file — on site or on board '
        'the vessel.',
    ),
]

# ─────────────────────────────────────────────── پرسش‌های متداول
# (پرسش فا، پرسش en، پاسخ فا، پاسخ en)

FAQS = [
    (
        'برای استعلام قیمت چه اطلاعاتی لازم است؟',
        'What information do you need for a quote?',
        'مشخصات فنی یا نقشه‌ی قطعه، تعداد، استاندارد یا گرید مورد نیاز، محل تحویل و '
        'زمان‌بندی پروژه. هرچه اطلاعات کامل‌تر باشد، پاسخ دقیق‌تر و سریع‌تر خواهد بود.',
        'The technical specification or drawing, quantity, required standard or grade, '
        'delivery location and project timeline. The more complete the information, the more '
        'accurate and faster our answer will be.',
    ),
    (
        'آیا امکان ساخت قطعه بر اساس نمونه یا نقشه وجود دارد؟',
        'Can you manufacture a part from a sample or drawing?',
        'بله. قطعات فلزی و پلیمری را بر اساس نقشه، نمونه‌ی موجود یا مشخصات فنی می‌سازیم. '
        'پس از بررسی نمونه یا نقشه، امکان‌پذیری، زمان و هزینه را اعلام می‌کنیم.',
        'Yes. We make metal and polymer parts to a drawing, an existing sample or a technical '
        'specification. After reviewing the sample or drawing, we confirm feasibility, lead '
        'time and cost.',
    ),
    (
        'محصولات همراه با چه مدارکی تحویل می‌شوند؟',
        'What documents come with delivered products?',
        'بسته به نوع محصول و الزامات پروژه، مدارک فنی، نتایج کنترل و آزمون و سوابق تأمین '
        'یا تولید همراه کالا ارائه می‌شود. پیش از سفارش، مدارک مورد نیاز پروژه‌ی خود را با '
        'ما در میان بگذارید.',
        'Depending on the product and the project’s requirements, technical documents, '
        'inspection and test results, and sourcing or production records are supplied with '
        'the goods. Please share your project’s documentation requirements with us before '
        'ordering.',
    ),
    (
        'آیا کالا را به شناور یا سکوی فراساحل هم تحویل می‌دهید؟',
        'Do you deliver to vessels or offshore platforms?',
        'بله. تحویل کالا به شناورها و پروژه‌های فراساحل، حمل بین‌المللی و امور گمرکی در '
        'ایران و امارات متحده عربی بخشی از خدمات ماست.',
        'Yes. Delivery to vessels and offshore projects, international shipping and customs '
        'clearance in Iran and the United Arab Emirates are all part of our services.',
    ),
    (
        'در انتخاب تجهیزات لیفتینگ و ریگینگ راهنمایی می‌کنید؟',
        'Can you help us choose lifting and rigging equipment?',
        'بله. بر اساس نوع بار، شرایط محیطی (دریایی/فراساحل) و استانداردهای ایمنی پروژه، '
        'تجهیزات مناسب را پیشنهاد می‌کنیم تا ریسک خرید نادرست کاهش یابد و عمر مفید '
        'تجهیزات افزایش پیدا کند.',
        'Yes. Based on the type of load, the environment (marine/offshore) and the project’s '
        'safety standards, we recommend suitable equipment — reducing the risk of a wrong '
        'purchase and extending equipment service life.',
    ),
]

# ─────────────────────────────────────────────── خطوط محصول
# (نامک، نام فا، نام en، توضیح فا، توضیح en، آیکون)

CATEGORIES = [
    (
        'marine-oil-gas-equipment',
        'تجهیزات صنعت دریا، نفت و گاز', 'Marine, Oil & Gas Equipment',
        'قطعات مکانیکی و هیدرولیکی و تجهیزات سنگین دریایی، متناسب با الزامات فنی '
        'پروژه‌های فراساحل.',
        'Mechanical and hydraulic components and heavy marine equipment, matched to the '
        'technical requirements of offshore projects.',
        'icon-wrench',
    ),
    (
        'lifting-rigging-equipment',
        'اقلام لیفتینگ و ریگینگ', 'Lifting & Rigging Equipment',
        'مجموعه کامل تجهیزات اتصال، بالابری و مهار بار، با استاندارد صنعتی بین‌المللی.',
        'A complete range of connecting, lifting and load-securing equipment, built to '
        'international industrial standards.',
        'icon-weight',
    ),
]

# ─────────────────────────────────────────────── محصولات
# (نامک، خط محصول، نام فا، نام en، توضیح کوتاه فا، توضیح کوتاه en، شاخص،
#  نامک‌های حوزه‌ی فعالیت، نامک‌های صنعت)

LIFTING_TECH = ('industrial-sourcing', 'quality-control-testing', 'documentation-traceability')
LIFTING_IND = ('offshore-oil-gas', 'marine-shipping', 'heavy-lift-pipeline')

PRODUCTS = [
    (
        'hydraulic-mechanical-components', 'marine-oil-gas-equipment',
        'قطعات هیدرولیکی و مکانیکی تخصصی', 'Specialised hydraulic and mechanical components',
        'تأمین و ساخت قطعات هیدرولیکی و مکانیکی مطابق مشخصات فنی و الزامات پروژه‌های '
        'فراساحل.',
        'Hydraulic and mechanical parts, sourced or manufactured to the technical '
        'specification and requirements of offshore projects.',
        True,
        ('industrial-sourcing', 'metal-polymer-manufacturing', 'quality-control-testing'),
        ('offshore-oil-gas', 'process-manufacturing'),
    ),
    (
        'heavy-marine-equipment', 'marine-oil-gas-equipment',
        'تجهیزات سنگین دریایی (Heavy Marine Equipment)', 'Heavy marine equipment',
        'تجهیزات سنگین مورد نیاز شناورها و پروژه‌های دریایی، متناسب با الزامات فنی پروژه.',
        'Heavy equipment for vessels and marine projects, matched to each project’s '
        'technical requirements.',
        True,
        ('industrial-sourcing', 'mechanical-electrical-assembly', 'logistics-offshore-delivery'),
        ('offshore-oil-gas', 'marine-shipping'),
    ),
    (
        'marine-platform-spare-parts', 'marine-oil-gas-equipment',
        'قطعات یدکی تجهیزات دریایی و سکوهای نفتی',
        'Spare parts for marine equipment and oil platforms',
        'قطعات یدکی برای تجهیزات دریایی و سکوهای نفتی، با تمرکز بر تطابق فنی و زمان '
        'تحویل.',
        'Spare parts for marine equipment and oil platforms, with a focus on technical '
        'compatibility and delivery time.',
        False,
        ('industrial-sourcing', 'logistics-offshore-delivery'),
        ('offshore-oil-gas', 'marine-shipping'),
    ),
    (
        'shackles', 'lifting-rigging-equipment',
        'شکل (Shackles)', 'Shackles',
        'انواع Bow، Dee، Screw Pin و Safety Pin',
        'Bow, Dee, Screw Pin and Safety Pin types',
        True, LIFTING_TECH, LIFTING_IND,
    ),
    (
        'hooks', 'lifting-rigging-equipment',
        'هوک (Hooks)', 'Hooks',
        'هوک‌های بار با قفل ایمنی',
        'Load hooks with safety latches',
        False, LIFTING_TECH, LIFTING_IND,
    ),
    (
        'blocks-sheaves', 'lifting-rigging-equipment',
        'بلاک و قرقره (Blocks & Sheaves)', 'Blocks & Sheaves',
        'برای سیستم‌های بالابری چندبخشی',
        'For multi-part lifting systems',
        False, LIFTING_TECH, LIFTING_IND,
    ),
    (
        'slings-grommets', 'lifting-rigging-equipment',
        'اسلینگ و گرومت (Sling & Grommet)', 'Slings & Grommets',
        'مهار بار انعطاف‌پذیر برای بارهای نامنظم',
        'Flexible load securing for irregular loads',
        False, LIFTING_TECH, LIFTING_IND,
    ),
    (
        'wire-rope', 'lifting-rigging-equipment',
        'وایر و طناب سیم فولادی (Wire Rope)', 'Wire Rope',
        'انواع وایر با گرید و قطر متناسب با بار مجاز',
        'Wire rope in grades and diameters matched to the working load limit',
        False, LIFTING_TECH, LIFTING_IND,
    ),
    (
        'winches', 'lifting-rigging-equipment',
        'وینچ (Winches)', 'Winches',
        'تجهیزات کشش و جابه‌جایی بار سنگین',
        'Pulling and handling equipment for heavy loads',
        False, LIFTING_TECH, LIFTING_IND,
    ),
    (
        'turnbuckles-swivels', 'lifting-rigging-equipment',
        'ترن‌باکل و سوییول (Turnbuckles & Swivels)', 'Turnbuckles & Swivels',
        'تنظیم کشش و جلوگیری از پیچش بار',
        'Tension adjustment and prevention of load twisting',
        False, LIFTING_TECH, LIFTING_IND,
    ),
]


def _both(obj, field, value_fa, value_en):
    """مقدار فارسی (زبان پیش‌فرض، ستون اصلی) و انگلیسی یک فیلد ترجمه‌پذیر را می‌نشاند."""
    setattr(obj, field, value_fa)
    setattr(obj, f'{field}_fa', value_fa)
    setattr(obj, f'{field}_en', value_en)


class Command(BaseCommand):
    help = 'بارگذاری محتوای نهایی کارفرما (فارسی و انگلیسی) و غیرفعال‌کردن محتوای آزمایشی.'

    @transaction.atomic
    def handle(self, *args, **options):
        company = CompanyInfo.objects.first()
        if company is None:
            raise CommandError('رکورد «اطلاعات شرکت» وجود ندارد؛ ابتدا آن را از پنل مدیریت بسازید.')

        with translation.override(settings.LANGUAGE_CODE):
            self._load_company(company)
            technologies = self._load_pages(Technology, TECHNOLOGIES, with_body=True)
            industries = self._load_pages(Industry, INDUSTRIES, with_body=False)
            self._load_blocks(Advantage, ADVANTAGES)
            self._load_blocks(Capability, CAPABILITIES)
            self._load_blocks(Service, SERVICES)
            self._load_statistics()
            self._load_process()
            self._load_faqs()
            self._load_products(technologies, industries)

        self.stdout.write(self.style.SUCCESS('محتوای نهایی کارفرما بارگذاری شد.'))

    def _report(self, model, kept, hidden):
        self.stdout.write(
            f'  {model._meta.verbose_name_plural}: {kept} مورد فعال'
            + (f'، {hidden} مورد آزمایشی غیرفعال شد' if hidden else '')
        )

    # ── اطلاعات شرکت ────────────────────────────────────────────────
    def _load_company(self, company):
        for field, (value_fa, value_en) in COMPANY.items():
            _both(company, field, value_fa, value_en)

        # تصاویر فقط یک بار کپی می‌شوند تا اجرای دوباره فایل تکراری در media نسازد.
        for field, rel_path in COMPANY_IMAGES.items():
            source = Path(settings.BASE_DIR) / 'static' / rel_path
            fieldfile = getattr(company, field)
            if fieldfile and Path(fieldfile.name).stem.startswith(source.stem):
                continue
            with source.open('rb') as handle:
                fieldfile.save(source.name, File(handle), save=False)

        company.save()
        self.stdout.write('  اطلاعات شرکت به‌روز شد.')

    # ── حوزه‌های فعالیت و صنعت‌ها ───────────────────────────────────
    def _load_pages(self, model, rows, with_body):
        by_slug = {}
        for index, row in enumerate(rows, start=1):
            if with_body:
                slug, title_fa, title_en, desc_fa, desc_en, body_fa, body_en, icon = row
            else:
                slug, title_fa, title_en, desc_fa, desc_en, icon = row
                body_fa = body_en = ''
            obj = model.objects.filter(slug=slug).first() or model(slug=slug)
            _both(obj, 'title', title_fa, title_en)
            _both(obj, 'description', desc_fa, desc_en)
            _both(obj, 'body', body_fa, body_en)
            _both(obj, 'meta_description', '', '')
            obj.icon, obj.order, obj.is_active = icon, index * 10, True
            obj.save()
            by_slug[slug] = obj

        hidden = model.objects.exclude(slug__in=by_slug).filter(is_active=True).update(is_active=False)
        self._report(model, len(by_slug), hidden)
        return by_slug

    # ── بلوک‌های ساده ───────────────────────────────────────────────
    def _load_blocks(self, model, rows):
        titles = []
        for index, (title_fa, title_en, desc_fa, desc_en, icon) in enumerate(rows, start=1):
            obj = model.objects.filter(title_fa=title_fa).first() or model()
            _both(obj, 'title', title_fa, title_en)
            _both(obj, 'description', desc_fa, desc_en)
            obj.icon, obj.order, obj.is_active = icon, index * 10, True
            obj.save()
            titles.append(title_fa)

        hidden = model.objects.exclude(title_fa__in=titles).filter(is_active=True).update(is_active=False)
        self._report(model, len(titles), hidden)

    def _load_statistics(self):
        labels = []
        for index, (value, label_fa, label_en) in enumerate(STATISTICS, start=1):
            obj = Statistic.objects.filter(label_fa=label_fa).first() or Statistic()
            obj.value = value
            _both(obj, 'label', label_fa, label_en)
            _both(obj, 'suffix', '', '')
            obj.order, obj.is_active = index * 10, True
            obj.save()
            labels.append(label_fa)

        hidden = Statistic.objects.exclude(label_fa__in=labels).filter(is_active=True).update(is_active=False)
        self._report(Statistic, len(labels), hidden)

    def _load_process(self):
        # مراحل بر پایه‌ی شماره‌ی مرحله به‌روز می‌شوند (نه ساخت رکورد تازه).
        numbers = []
        for number, title_fa, title_en, desc_fa, desc_en in PROCESS:
            obj = ProcessStep.objects.filter(step_number=number).first() or ProcessStep(step_number=number)
            _both(obj, 'title', title_fa, title_en)
            _both(obj, 'description', desc_fa, desc_en)
            obj.is_active = True
            obj.save()
            numbers.append(number)

        hidden = ProcessStep.objects.exclude(step_number__in=numbers).filter(is_active=True).update(is_active=False)
        self._report(ProcessStep, len(numbers), hidden)

    def _load_faqs(self):
        questions = []
        for index, (q_fa, q_en, a_fa, a_en) in enumerate(FAQS, start=1):
            obj = FAQ.objects.filter(question_fa=q_fa).first() or FAQ()
            _both(obj, 'question', q_fa, q_en)
            _both(obj, 'answer', a_fa, a_en)
            obj.order, obj.is_active = index * 10, True
            obj.save()
            questions.append(q_fa)

        hidden = FAQ.objects.exclude(question_fa__in=questions).filter(is_active=True).update(is_active=False)
        self._report(FAQ, len(questions), hidden)

    # ── خطوط محصول و محصولات ────────────────────────────────────────
    def _load_products(self, technologies, industries):
        categories = {}
        for index, (slug, name_fa, name_en, desc_fa, desc_en, icon) in enumerate(CATEGORIES, start=1):
            obj = Category.objects.filter(slug=slug).first() or Category(slug=slug)
            _both(obj, 'name', name_fa, name_en)
            _both(obj, 'description', desc_fa, desc_en)
            obj.icon, obj.order = icon, index * 10
            obj.save()
            categories[slug] = obj

        slugs = []
        for index, row in enumerate(PRODUCTS, start=1):
            (slug, category_slug, name_fa, name_en, short_fa, short_en,
             featured, tech_slugs, industry_slugs) = row
            category = categories[category_slug]
            obj = Product.objects.filter(slug=slug).first() or Product(slug=slug)
            obj.category = category
            _both(obj, 'name', name_fa, name_en)
            _both(obj, 'short_description', short_fa, short_en)
            # توضیح کامل: توضیح خود قلم + توضیح خط محصول (هر دو از متن کارفرما).
            _both(
                obj, 'description',
                f'{short_fa}\n\n{category.description_fa}',
                f'{short_en}\n\n{category.description_en}',
            )
            obj.is_active, obj.is_featured, obj.order = True, featured, index * 10
            obj.save()
            obj.technologies.set([technologies[s] for s in tech_slugs])
            obj.industries.set([industries[s] for s in industry_slugs])
            slugs.append(slug)

        hidden = Product.objects.exclude(slug__in=slugs).filter(is_active=True).update(is_active=False)
        self._report(Product, len(slugs), hidden)

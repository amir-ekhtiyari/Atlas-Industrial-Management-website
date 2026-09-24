"""
محتوای اولیه‌ی سایت — ساختار «شرکت‌محور».

قواعدی که در نوشتن این متن‌ها رعایت شده و باید رعایت بماند:

* هیچ گواهی‌نامه، تأییدیه، مشتری، جایزه، عدد تولید یا سهم بازار جعلی نوشته
  نشده است. مدل‌های «استاندارد/گواهی‌نامه»، «آمار» و «نقاط عطف» عمداً خالی
  می‌مانند تا فقط داده‌ی واقعی شرکت از پنل مدیریت وارد شود.
* متن‌ها درباره‌ی *شرکت* و *توانمندی‌ها* است، نه یک محصول خاص. هر محصولی که
  از پنل اضافه شود، به‌طور خودکار در ساختار جای می‌گیرد.
* اعداد فنی محصول (دبی، وزن، فشار، مدت) نوشته نمی‌شود؛ اینها را تیم فنی
  شرکت وارد می‌کند.

دستور idempotent است: رکوردهای موجود دست‌نخورده می‌مانند.

    python manage.py seed_site_content
    python manage.py seed_site_content --flush   # بازنویسی بلوک‌های محتوایی
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Advantage,
    Capability,
    CompanyInfo,
    FAQ,
    Industry,
    ProcessStep,
    Service,
    Technology,
)

# ─────────────────────────────────────────────── حوزه‌های فناوری
# (عنوان فا، عنوان en، نامک، توضیح فا، توضیح en، متن صفحه فا، متن صفحه en، آیکون)

TECHNOLOGIES = [
    (
        'سیستم‌های گاز تحت فشار', 'Pressurised gas systems', 'pressurised-gas-systems',
        'طراحی مسیر گاز، تنظیم فشار و کنترل جریان در تجهیزاتی که باید سال‌ها '
        'آماده‌به‌کار بمانند و در لحظه‌ی لازم بدون خطا کار کنند.',
        'Gas path design, pressure regulation and flow control for equipment that must '
        'stay on standby for years and work without fault the moment it is needed.',
        'این حوزه هسته‌ی بخش بزرگی از کار ماست: طراحی و کالیبراسیون مسیری که گاز '
        'از منبع تا نقطه‌ی مصرف طی می‌کند.\n\n'
        'کار ما شامل انتخاب و ارزیابی اجزای تحت فشار، طراحی رگولاتور و مسیر '
        'خروجی، آزمون نشتی روی هر واحد و اندازه‌گیری پارامترهای عملکردی است. '
        'نتیجه‌ی آزمون هر واحد در پرونده‌ی شماره سری همان واحد ثبت می‌شود.\n\n'
        'در تجهیزاتی که دوره‌ی آماده‌به‌کاری طولانی دارند، پایداری در طول زمان '
        'به‌اندازه‌ی عملکرد لحظه‌ای مهم است؛ همین موضوع انتخاب مواد و روش '
        'مونتاژ را تعیین می‌کند.',
        'This area sits at the centre of much of our work: designing and calibrating the '
        'path gas travels from source to point of use.\n\n'
        'It covers selection and evaluation of pressure-bearing components, regulator and '
        'outlet design, leak testing on every unit, and measurement of functional '
        'parameters. Test results for each unit are recorded in the file of that serial '
        'number.\n\n'
        'In equipment with long standby periods, stability over time matters as much as '
        'instantaneous performance — and that governs material selection and assembly '
        'method.',
        'icon-gauge',
    ),
    (
        'تجهیزات ایمنی و اضطراری', 'Safety and emergency equipment', 'safety-emergency-equipment',
        'ساخت تجهیزاتی که در شرایط اضطراری باید بی‌درنگ و بدون آماده‌سازی وارد '
        'سرویس شوند — با تمرکز بر قابلیت اطمینان و سادگی استفاده.',
        'Building equipment that must enter service immediately and without preparation in '
        'an emergency — designed around reliability and simplicity of use.',
        'تجهیز اضطراری منطق طراحی خاص خودش را دارد: کسی که از آن استفاده می‌کند '
        'فرصت خواندن دستورالعمل ندارد و ممکن است آموزش تخصصی هم نداشته باشد.\n\n'
        'بنابراین طراحی حول سه چیز شکل می‌گیرد: کوتاه‌کردن مسیر ورود به سرویس، '
        'کاهش تعداد اقدام‌های لازم، و روشن بودن وضعیت آماده‌به‌کاری دستگاه با '
        'یک نگاه. هر تصمیم طراحی که این سه را تضعیف کند، حتی اگر از نظر فنی '
        'جذاب باشد، کنار گذاشته می‌شود.',
        'Emergency equipment follows its own design logic: whoever uses it has no time to '
        'read instructions and may have no specialist training.\n\n'
        'So the design turns on three things: shortening the path into service, reducing '
        'the number of required actions, and making standby status readable at a glance. '
        'Any design decision that weakens those three is set aside, however technically '
        'appealing it may be.',
        'icon-shield',
    ),
    (
        'طراحی فشرده و سبک', 'Compact, low-mass design', 'compact-low-mass-design',
        'کاهش وزن و حجم بدون کاستن از قابلیت اطمینان — الزام همیشگی تجهیزاتی که '
        'در فضای محدود نصب یا حمل می‌شوند.',
        'Reducing mass and volume without reducing reliability — the standing constraint on '
        'equipment installed or carried in a confined envelope.',
        'در بسیاری از کاربردهایی که با آن‌ها کار می‌کنیم، وزن و حجم هزینه‌ی '
        'واقعی دارند. یک تجهیز سنگین‌تر یا حجیم‌تر ممکن است اصلاً قابل نصب نباشد.\n\n'
        'کار ما در این حوزه بازچینی اجزا برای کوچک‌کردن پوسته، انتخاب مواد با '
        'نسبت استحکام به وزن مناسب، و حذف هر جزئی است که نقش عملکردی روشنی '
        'ندارد. این کار برخلاف کاهش کیفیت است: کمتر کردن اجزا به معنای کمتر '
        'شدن نقاط خرابی احتمالی هم هست.',
        'In many of the applications we work on, mass and volume carry a real cost. A '
        'heavier or bulkier unit may simply not be installable.\n\n'
        'Our work here means rearranging components to shrink the envelope, selecting '
        'materials with an appropriate strength-to-weight ratio, and removing any part '
        'without a clear functional role. This is the opposite of cutting quality: fewer '
        'parts also means fewer possible failure points.',
        'icon-weight',
    ),
    (
        'آزمون و کنترل کیفیت', 'Testing and quality control', 'testing-quality-control',
        'اندازه‌گیری عملکرد، آزمون نشتی و ثبت مستند نتایج برای هر واحد پیش از '
        'تحویل — چون کیفیت باید قابل اثبات باشد.',
        'Performance measurement, leak testing and documented results for every unit before '
        'delivery — because quality has to be demonstrable.',
        'برای تجهیزاتی که در شرایط پرالزام کار می‌کنند، «آزمون شده» یعنی هر '
        'واحد، نه یک نمونه از هر دسته.\n\n'
        'هر واحد پیش از تحویل آزمون عملکرد و نشتی را طی می‌کند و نتیجه در '
        'پرونده‌ی شماره سری همان واحد ثبت می‌شود. این پرونده هنگام ارزیابی، '
        'مبنای گفت‌وگوی فنی با تیم مشتری است.\n\n'
        'مستندسازی برای ما بخشی از محصول است، نه کار اداری پس از آن.',
        'For equipment that works in demanding conditions, “tested” must mean every unit, '
        'not one sample per batch.\n\n'
        'Each unit passes functional and leak testing before delivery, and the result is '
        'recorded in the file of that serial number. During evaluation, that file is the '
        'basis of the technical discussion with your team.\n\n'
        'For us documentation is part of the product, not paperwork that follows it.',
        'icon-flask',
    ),
    (
        'مهندسی مواد', 'Materials engineering', 'materials-engineering',
        'انتخاب و ارزیابی مواد سازگار با شرایط کاری — از سازگاری شیمیایی تا '
        'دوام در چرخه‌های حرارتی و فشاری.',
        'Selecting and evaluating materials for the service conditions — from chemical '
        'compatibility to durability through thermal and pressure cycles.',
        'انتخاب ماده در تجهیزات فنی یک تصمیم یک‌باره نیست؛ باید با شرایط کاری، '
        'ماده‌ی در تماس، دامنه‌ی دمایی و طول دوره‌ی بهره‌برداری سنجیده شود.\n\n'
        'ما برای هر کاربرد، سازگاری مواد را بررسی و گزینه‌ها را در شرایط نزدیک '
        'به کار واقعی ارزیابی می‌کنیم. جایی که داده‌ی کافی در دست نباشد، آزمون '
        'می‌گیریم و نتیجه را مستند می‌کنیم.',
        'Material selection in technical equipment is not a one-off decision; it has to be '
        'weighed against service conditions, the medium in contact, temperature range and '
        'the length of the operating life.\n\n'
        'For each application we review material compatibility and evaluate options under '
        'conditions close to real service. Where the available data is insufficient, we '
        'test and document the result.',
        'icon-layers',
    ),
    (
        'ساخت و مونتاژ دقیق', 'Precision fabrication and assembly', 'precision-fabrication',
        'ساخت قطعات و مونتاژ نهایی در مجموعه‌ی خودمان؛ چرخه‌ی اصلاح کوتاه و '
        'پاسخ فنی مستقیم.',
        'Part fabrication and final assembly in our own facility: short iteration cycles '
        'and direct technical answers.',
        'ساخت در مجموعه‌ی خودمان یک مزیت عملی دارد: وقتی نتیجه‌ی آزمون نشان '
        'می‌دهد جزئی باید تغییر کند، تغییر را همان‌جا اعمال می‌کنیم و دوباره '
        'آزمون می‌گیریم.\n\n'
        'همین موضوع باعث می‌شود پاسخ به پرسش فنی تیم مشتری از خود کسی بیاید که '
        'قطعه را ساخته است، نه از یک واسطه.',
        'Building in our own facility has a practical advantage: when a test result shows a '
        'part needs to change, we make the change on the spot and test again.\n\n'
        'It also means the answer to your engineers’ technical question comes from the '
        'people who made the part, not from an intermediary.',
        'icon-factory',
    ),
]
# ───────────────────────────────────────────────── صنعت‌ها
INDUSTRIES = [
    (
        'هوانوردی', 'Aviation', 'aviation',
        'تجهیزات ایمنی و اضطراری برای کاربردهای هوایی، جایی که وزن، حجم و '
        'قابلیت اطمینان هم‌زمان محدودکننده‌اند.',
        'Safety and emergency equipment for aviation applications, where mass, volume and '
        'reliability constrain the design at the same time.',
        'هوانوردی امروز بزرگ‌ترین حوزه‌ی فعالیت ماست. الزامات این صنعت روشن و '
        'سختگیرانه است: تجهیز باید سبک باشد، در پوسته‌ی محدودی جا شود، '
        'دوره‌های طولانی بدون استفاده آماده بماند و در لحظه‌ی لازم بدون خطا '
        'کار کند.\n\n'
        'مشتریان ما در این حوزه شرکت‌های هوایی، سازمان‌ها و مجموعه‌های صنعتی '
        'مرتبط با هوانوردی هستند. الزامات تأییدیه در هر بازار و برای هر ناوگان '
        'متفاوت است؛ ما مدارک فنی موجود را ارائه می‌کنیم تا مسیر لازم با هم '
        'مشخص شود.',
        'Aviation is currently our largest area of activity. Its requirements are explicit '
        'and strict: equipment must be light, fit a tight envelope, remain ready through '
        'long periods without use, and work without fault at the moment it is needed.\n\n'
        'Our customers here are airlines, organisations and aviation-related industrial '
        'operations. Approval requirements differ by market and by fleet; we provide the '
        'technical documentation we hold so the required path can be mapped out together.',
        'icon-aircraft',
    ),
    (
        'صنایع تولیدی', 'Industrial manufacturing', 'industrial-manufacturing',
        'تجهیزات فنی برای فرایندهایی که به تأمین پیوسته و پایدار نیاز دارند.',
        'Technical equipment for processes that need continuous, stable supply.',
        'همان توانمندی‌هایی که در تجهیزات هوایی به کار می‌آید — طراحی مسیر '
        'گاز، تنظیم فشار، آزمون و مستندسازی — در محیط‌های صنعتی هم کاربرد '
        'دارد.\n\n'
        'در این حوزه با مجموعه‌هایی کار می‌کنیم که به تجهیزات با دوره‌ی '
        'بهره‌برداری طولانی و پشتیبانی قابل اتکا نیاز دارند.',
        'The same capabilities that serve aviation equipment — gas path design, pressure '
        'regulation, testing and documentation — apply in industrial environments too.\n\n'
        'Here we work with operations that need equipment with a long service life and '
        'dependable support behind it.',
        'icon-factory',
    ),
    (
        'حوزه‌ی درمان', 'Healthcare', 'healthcare',
        'تجهیزات مرتبط با تأمین گاز تنفسی در محیط‌های درمانی و امدادی.',
        'Equipment related to breathable gas supply in clinical and emergency-response '
        'settings.',
        'محیط درمانی الزامات خاصی برای پاکی مسیر، سازگاری مواد و قابلیت اطمینان '
        'دارد. توان مهندسی ما در سیستم‌های گاز تحت فشار در این حوزه هم قابل '
        'استفاده است.\n\n'
        'برای گفت‌وگو درباره‌ی نیاز مشخص خود در این حوزه با ما تماس بگیرید.',
        'Clinical settings impose specific requirements on path cleanliness, material '
        'compatibility and reliability. Our engineering capacity in pressurised gas systems '
        'is applicable here as well.\n\n'
        'Contact us to discuss a specific requirement in this area.',
        'icon-hospital',
    ),
    (
        'پژوهش و آزمایشگاه', 'Research and laboratory', 'research-laboratory',
        'تجهیزات و تأمین گاز برای مصارف پژوهشی و آزمایشگاهی.',
        'Equipment and gas supply for research and laboratory use.',
        'کاربردهای آزمایشگاهی معمولاً به دقت اندازه‌گیری و پایداری در '
        'بازه‌های طولانی نیاز دارند تا نتایج تکرارپذیر باشند.\n\n'
        'در این حوزه با مراکز پژوهشی و آزمایشگاه‌هایی کار می‌کنیم که به '
        'پیکربندی خاص خودشان نیاز دارند.',
        'Laboratory applications typically require measurement accuracy and long-interval '
        'stability so that results stay reproducible.\n\n'
        'Here we work with research centres and laboratories that need a configuration '
        'specific to their setup.',
        'icon-flask',
    ),
]

# ───────────────────────────────────────────────── تمایزها
ADVANTAGES = [
    ('طراحی و ساخت در یک مجموعه', 'Design and build under one roof',
     'طراحی، مونتاژ و آزمون در مجموعه‌ی خودمان انجام می‌شود. نتیجه‌اش چرخه‌ی '
     'اصلاح کوتاه‌تر و پاسخ فنی مستقیم به تیم مهندسی مشتری است.',
     'Design, assembly and testing take place in our own facility. That means shorter '
     'iteration cycles and direct technical answers for your engineers.',
     'icon-factory'),

    ('تخصص متمرکز', 'A focused specialisation',
     'توان مهندسی ما روی دسته‌ای محدود و پرالزام از تجهیزات فنی متمرکز است، '
     'نه سبدی گسترده از محصولات عمومی.',
     'Our engineering capacity is concentrated on a narrow, demanding class of technical '
     'equipment rather than a broad catalogue of general products.',
     'icon-target'),

    ('ساختار هزینه‌ی رقابتی', 'A competitive cost structure',
     'ساختار تولید ما اجازه می‌دهد در دسته‌هایی که تنها شمار محدودی سازنده‌ی '
     'تخصصی در جهان دارند، قیمت رقابتی ارائه کنیم.',
     'Our production structure lets us offer competitive pricing in categories served by '
     'only a small number of specialised manufacturers worldwide.',
     'icon-chart'),

    ('شفافیت فنی', 'Technical transparency',
     'داده‌ی فنی و سابقه‌ی آزمون هر واحد برای بررسی تیم مشتری تهیه می‌شود؛ '
     'ارزیابی باید بر پایه‌ی مدرک باشد، نه ادعا.',
     'Technical data and per-unit test records are prepared for your review. Evaluation '
     'should rest on documentation, not on claims.',
     'icon-clipboard'),
]
# ───────────────────────────────────────────── توانمندی‌ها
CAPABILITIES = [
    ('مهندسی طراحی', 'Design engineering',
     'طراحی مکانیکی و سیالاتی از مفهوم تا نقشه‌ی ساخت.',
     'Mechanical and fluid design from concept to manufacturing drawing.',
     'icon-cog'),
    ('ساخت قطعه', 'Part fabrication',
     'ساخت قطعات در کارگاه مجموعه، بدون وابستگی به واسطه.',
     'Parts produced in our own workshop, without dependence on an intermediary.',
     'icon-wrench'),
    ('مونتاژ کنترل‌شده', 'Controlled assembly',
     'مونتاژ در محیط کنترل‌شده با رویه‌ی مکتوب.',
     'Assembly in a controlled environment following a written procedure.',
     'icon-factory'),
    ('آزمون عملکرد', 'Performance testing',
     'اندازه‌گیری پارامترهای کاری و آزمون نشتی روی هر واحد.',
     'Operating parameters measured and leak testing performed on every unit.',
     'icon-flask'),
    ('مستندسازی', 'Documentation',
     'پرونده‌ی فنی برای هر شماره سری، شامل نتیجه‌ی آزمون.',
     'A technical file for each serial number, including test results.',
     'icon-clipboard'),
    ('پشتیبانی فنی', 'Technical support',
     'پاسخ‌گویی مهندسی پس از تحویل و در دوره‌ی بهره‌برداری.',
     'Engineering support after delivery and through the service life.',
     'icon-headset'),
]

# ───────────────────────────────────────────────── خدمات
SERVICES = [
    ('مشاوره و انتخاب پیکربندی', 'Consultation and configuration',
     'بررسی نیاز و پیشنهاد پیکربندی مناسب پیش از هر تعهد خرید.',
     'We review the requirement and propose a suitable configuration before any purchase '
     'commitment.',
     'icon-headset'),
    ('تأمین و تحویل', 'Supply and delivery',
     'برنامه‌ی تأمین، بسته‌بندی مناسب حمل و هماهنگی تحویل.',
     'Supply planning, transport-appropriate packaging and delivery coordination.',
     'icon-route'),
    ('آموزش کاربری', 'Operator training',
     'آموزش استفاده و نگهداری برای تیم عملیات.',
     'Use and upkeep training for the operating team.',
     'icon-users'),
    ('پشتیبانی و قطعات', 'Support and spares',
     'پشتیبانی فنی پس از تحویل و تأمین قطعات مصرفی.',
     'Post-delivery technical support and consumable supply.',
     'icon-wrench'),
]

# ─────────────────────────────────────────── فرایند همکاری
PROCESS = [
    (1, 'بررسی نیاز', 'Requirement review',
     'کاربری مورد نظر، شرایط کاری و الزامات بازار مقصد را با هم مرور می‌کنیم.',
     'We review the intended use case, service conditions and the requirements of your '
     'target market.'),
    (2, 'ارائه‌ی بسته‌ی داده‌ی فنی', 'Technical data package',
     'مشخصات، مدارک فنی و شرایط تحویل به‌صورت مکتوب در اختیار تیم شما قرار می‌گیرد.',
     'Specifications, technical documents and delivery terms are provided to your team in '
     'writing.'),
    (3, 'ارزیابی نمونه', 'Sample evaluation',
     'در صورت نیاز، واحد نمونه برای ارزیابی مستقل تیم مهندسی مشتری ارسال می‌شود.',
     'Where required, a sample unit is supplied so your engineers can evaluate it '
     'independently.'),
    (4, 'سفارش، تحویل و پشتیبانی', 'Order, delivery and support',
     'پس از توافق، برنامه‌ی تولید و تحویل تنظیم و پشتیبانی دوره‌ای آغاز می‌شود.',
     'Once agreed, we set the production and delivery schedule and begin ongoing support.'),
]

# ─────────────────────────────────────────── پرسش‌های پرتکرار
FAQS = [
    ('برای شروع بررسی چه اطلاعاتی لازم است؟',
     'What information do you need to start?',
     'کاربری مورد نظر، شرایط کاری، تعداد تقریبی و بازار مقصد. با همین چهار مورد '
     'می‌توانیم گفت‌وگوی فنی را آغاز کنیم.',
     'The intended use case, service conditions, approximate quantity and target market. '
     'Those four points are enough to open a technical discussion.'),

    ('امکان ارزیابی نمونه وجود دارد؟',
     'Can we evaluate a sample?',
     'بله. درخواست خود را از فرم تماس ثبت کنید تا شرایط ارسال واحد نمونه برای '
     'ارزیابی بررسی شود.',
     'Yes. Submit a request through the contact form and we will discuss terms for '
     'supplying a sample unit for evaluation.'),

    ('مسیر تأییدیه و مدارک چگونه است؟',
     'How are approvals and documentation handled?',
     'الزامات تأییدیه به بازار و کاربری مقصد بستگی دارد و برای هر پروژه متفاوت '
     'است. مدارک فنی موجود را در اختیار تیم شما می‌گذاریم تا مسیر لازم را با هم '
     'مشخص کنیم.',
     'Approval requirements depend on the destination market and use case, and differ from '
     'project to project. We share the technical documentation we hold so the required path '
     'can be mapped out together.'),

    ('محصولی که لازم دارم در کاتالوگ نیست. چه کنم؟',
     'What if the product I need is not in the catalogue?',
     'نیاز خود را برای ما بنویسید. بخشی از کار ما توسعه‌ی تجهیز بر پایه‌ی '
     'الزامات مشخص مشتری است؛ بررسی می‌کنیم که آیا در محدوده‌ی توانمندی‌های '
     'فعلی ما هست یا نه.',
     'Tell us the requirement. Part of our work is developing equipment against a specific '
     'customer specification; we will assess whether it falls within our current '
     'capabilities.'),

    ('برای صادرات یا نمایندگی چگونه همکاری کنیم؟',
     'How can we discuss export or distribution?',
     'موضوع درخواست را «همکاری و نمایندگی» انتخاب کنید و بازار و حوزه‌ی فعالیت '
     'خود را بنویسید؛ تیم بازرگانی پاسخ می‌دهد.',
     'Select “Partnership and distribution” as the request type and tell us your market and '
     'area of activity; our commercial team will respond.'),
]
# ─────────────────────────────────── متن‌های شرکت (CompanyInfo)
COMPANY_DEFAULTS = {
    'tagline': (
        'مهندسی و تولید تجهیزات فنی',
        'Engineering and manufacturing of technical equipment',
    ),
    'hero_title': (
        'تجهیزات فنی برای کاربردهای پرالزام',
        'Technical equipment for demanding applications',
    ),
    'hero_text': (
        'اطلس یک شرکت مهندسی و تولیدی است که روی تجهیزات فنی کار می‌کند: '
        'جایی که قابلیت اطمینان، وزن و دوام هم‌زمان محدودکننده‌اند. طراحی، '
        'ساخت و آزمون در مجموعه‌ی خودمان انجام می‌شود و محصولات ما امروز در '
        'هوانوردی و صنایع مرتبط به کار می‌روند.',
        'Atlas is an engineering and manufacturing company working on technical equipment — '
        'where reliability, mass and durability constrain the design at the same time. '
        'Design, fabrication and testing happen in our own facility, and our products are '
        'in service today in aviation and related industries.',
    ),
    'intro_title': (
        'یک مجموعه، از طراحی تا پشتیبانی',
        'One team, from design to support',
    ),
    'intro_text': (
        'ما تجهیزاتی می‌سازیم که باید در شرایط دشوار کار کنند: سبک باشند، در '
        'فضای محدود جا شوند، دوره‌های طولانی آماده بمانند و در لحظه‌ی لازم '
        'بدون خطا عمل کنند.\n\n'
        'کل چرخه در مجموعه‌ی خودمان انجام می‌شود — طراحی، ساخت قطعه، مونتاژ، '
        'آزمون و پشتیبانی. همین یک‌پارچگی باعث می‌شود چرخه‌ی اصلاح کوتاه بماند '
        'و پاسخ فنی به تیم مهندسی مشتری از خود سازنده بیاید.',
        'We build equipment that has to work in difficult conditions: light, fitting a tight '
        'envelope, ready after long periods of standby, and functioning without fault at the '
        'moment it is needed.\n\n'
        'The whole cycle runs in our own facility — design, part fabrication, assembly, '
        'testing and support. That integration keeps iteration cycles short and means the '
        'technical answer your engineers receive comes from the people who built the part.',
    ),
    'about_text': (
        'اطلس یک شرکت مهندسی و تولیدی در حوزه‌ی تجهیزات فنی است. توان ما روی '
        'دسته‌ای متمرکز از تجهیزات قرار دارد که در آن‌ها قابلیت اطمینان، وزن و '
        'دوام هم‌زمان محدودکننده‌اند — به‌ویژه سیستم‌های گاز تحت فشار و '
        'تجهیزات ایمنی و اضطراری.\n\n'
        'امروز محصولات ما در هوانوردی و صنایع مرتبط به کار می‌روند و به شرکت‌ها، '
        'سازمان‌ها و مجموعه‌های صنعتی در ایران عرضه می‌شوند. توانمندی‌های فناورانه‌ی '
        'ما محدود به یک محصول نیست؛ هر محصول از همان حوزه‌های فناوری بیرون '
        'می‌آید و با گسترش این حوزه‌ها، خطوط محصول تازه شکل می‌گیرد.\n\n'
        'گام بعدی ما ورود سنجیده به بازارهای بین‌المللی است: با همان کیفیت '
        'مهندسی، ساختار هزینه‌ی رقابتی‌تر و مستندسازی فنی شفاف.',
        'Atlas is an engineering and manufacturing company in technical equipment. Our '
        'capability is concentrated on a class of equipment where reliability, mass and '
        'durability constrain the design at once — particularly pressurised gas systems and '
        'safety and emergency equipment.\n\n'
        'Our products are in service today in aviation and related industries, supplied to '
        'companies, organisations and industrial operations in Iran. Our technological '
        'capabilities are not limited to a single product: each product comes out of those '
        'same technology areas, and as the areas grow, new product lines follow.\n\n'
        'Our next step is a measured entry into international markets: the same engineering '
        'quality, a more competitive cost structure, and transparent technical '
        'documentation.',
    ),
    'mission_text': (
        'ساختن تجهیزات فنی قابل اعتماد برای کاربردهای پرالزام، با مستندات روشن '
        'و پشتیبانی پایدار در تمام دوره‌ی بهره‌برداری.',
        'To build dependable technical equipment for demanding applications, with clear '
        'documentation and steady support throughout its service life.',
    ),
    'vision_text': (
        'تبدیل شدن به یک تأمین‌کننده‌ی شناخته‌شده و قابل اتکا در حوزه‌های '
        'تخصصی تجهیزات فنی — بر پایه‌ی کیفیت ساخت و کیفیت پشتیبانی، نه بر '
        'پایه‌ی تبلیغ.',
        'To become a recognised, dependable supplier in specialised areas of technical '
        'equipment — on the strength of build quality and support quality, not marketing.',
    ),
    'global_title': (
        'آماده‌ی بازارهای بین‌المللی',
        'Ready for international markets',
    ),
    'global_text': (
        'در دسته‌هایی که ما در آن‌ها کار می‌کنیم، تنها شمار محدودی سازنده‌ی '
        'تخصصی در جهان فعال است؛ برای یک خریدار، ورود تأمین‌کننده‌ی تازه با '
        'ساختار هزینه‌ی رقابتی ارزش بررسی دارد.\n\n'
        'ما برای گفت‌وگو با شرکت‌ها، سازندگان، واردکنندگان و توزیع‌کنندگان '
        'بین‌المللی آماده‌ایم. الزامات هر بازار متفاوت است؛ ترجیح می‌دهیم مسیر '
        'فنی و بازرگانی را از ابتدا و به‌صورت شفاف با مشتری مرور کنیم.',
        'In the categories where we work, only a small number of specialised manufacturers '
        'operate worldwide. For a buyer, a new supplier with a competitive cost structure is '
        'worth evaluating.\n\n'
        'We are open to discussions with companies, manufacturers, importers and '
        'international distributors. Every market has different requirements, and we prefer '
        'to review the technical and commercial path openly from the start.',
    ),
    'cta_title': (
        'درباره‌ی پروژه‌ی خود با ما صحبت کنید',
        'Let’s talk about your project',
    ),
    'cta_text': (
        'نیاز فنی و بازار مقصد خود را برای ما بنویسید تا گزینه‌های ممکن، '
        'مشخصات و شرایط همکاری را بررسی کنیم.',
        'Tell us your technical requirement and target market, and we will review the '
        'available options, specifications and terms of cooperation with you.',
    ),
    'meta_description': (
        'اطلس — مهندسی و تولید تجهیزات فنی برای کاربردهای پرالزام؛ سیستم‌های '
        'گاز تحت فشار و تجهیزات ایمنی، طراحی و ساخته‌شده در ایران.',
        'Atlas — engineering and manufacturing of technical equipment for demanding '
        'applications: pressurised gas systems and safety equipment, designed and built in '
        'Iran.',
    ),
}
class Command(BaseCommand):
    help = 'ایجاد محتوای اولیه‌ی سایت (بدون تغییر رکوردهای موجود).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='حذف بلوک‌های محتوایی موجود و ساخت دوباره‌ی آن‌ها. '
                 'اطلاعات شرکت، محصولات و تیم دست‌نخورده می‌مانند.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            for model in (Technology, Industry, Advantage, Capability, Service, ProcessStep, FAQ):
                deleted, _ = model.objects.all().delete()
                self.stdout.write(f'  حذف {deleted} رکورد از {model._meta.verbose_name_plural}')

        created = 0
        created += self._seed_pages(Technology, TECHNOLOGIES)
        created += self._seed_pages(Industry, INDUSTRIES)
        created += self._seed_blocks(Advantage, ADVANTAGES)
        created += self._seed_blocks(Capability, CAPABILITIES)
        created += self._seed_blocks(Service, SERVICES)
        created += self._seed_process()
        created += self._seed_faqs()
        filled = self._fill_company_defaults()

        self.stdout.write(self.style.SUCCESS(f'{created} رکورد محتوایی ساخته شد.'))
        if filled:
            self.stdout.write(self.style.SUCCESS(
                'فیلدهای خالی اطلاعات شرکت پر شد: ' + ', '.join(filled)
            ))
        self.stdout.write(
            '\nعمداً پر نشده — این‌ها را خودتان از پنل مدیریت وارد کنید:\n'
            '  • محصولات و مشخصات فنی آن‌ها (اعداد واقعی: دبی، وزن، فشار، ابعاد)\n'
            '  • استانداردها و گواهی‌نامه‌ها — فقط مواردی که واقعاً دارید\n'
            '  • آمار و دستاوردها، و نقاط عطف (اعداد و تاریخ‌های واقعی شرکت)\n'
            '  • نظرات مشتریان\n'
            'تا زمانی که خالی باشند، آن بخش‌ها در سایت نمایش داده نمی‌شوند.'
        )

    def _seed_pages(self, model, rows):
        """مدل‌های دارای صفحه‌ی اختصاصی: فناوری و صنعت."""
        created = 0
        for index, row in enumerate(rows, start=1):
            title_fa, title_en, slug, desc_fa, desc_en, body_fa, body_en, icon = row
            if model.objects.filter(slug=slug).exists():
                continue
            model.objects.create(
                slug=slug, icon=icon, order=index * 10,
                title=title_fa, title_fa=title_fa, title_en=title_en,
                description=desc_fa, description_fa=desc_fa, description_en=desc_en,
                body=body_fa, body_fa=body_fa, body_en=body_en,
            )
            created += 1
        return created

    def _seed_blocks(self, model, rows):
        """بلوک‌های محتوایی ساده: تمایز، توانمندی، خدمت."""
        created = 0
        for index, (title_fa, title_en, desc_fa, desc_en, icon) in enumerate(rows, start=1):
            if model.objects.filter(title_fa=title_fa).exists():
                continue
            model.objects.create(
                icon=icon, order=index * 10,
                title=title_fa, title_fa=title_fa, title_en=title_en,
                description=desc_fa, description_fa=desc_fa, description_en=desc_en,
            )
            created += 1
        return created

    def _seed_process(self):
        created = 0
        for number, title_fa, title_en, desc_fa, desc_en in PROCESS:
            if ProcessStep.objects.filter(step_number=number).exists():
                continue
            ProcessStep.objects.create(
                step_number=number,
                title=title_fa, title_fa=title_fa, title_en=title_en,
                description=desc_fa, description_fa=desc_fa, description_en=desc_en,
            )
            created += 1
        return created

    def _seed_faqs(self):
        created = 0
        for index, (q_fa, q_en, a_fa, a_en) in enumerate(FAQS, start=1):
            if FAQ.objects.filter(question_fa=q_fa).exists():
                continue
            FAQ.objects.create(
                order=index * 10,
                question=q_fa, question_fa=q_fa, question_en=q_en,
                answer=a_fa, answer_fa=a_fa, answer_en=a_en,
            )
            created += 1
        return created

    def _fill_company_defaults(self):
        company = CompanyInfo.objects.first()
        if company is None:
            self.stdout.write(self.style.WARNING(
                'رکورد «اطلاعات شرکت» وجود ندارد؛ ابتدا آن را از پنل مدیریت بسازید.'
            ))
            return []

        touched = []
        for field, (value_fa, value_en) in COMPANY_DEFAULTS.items():
            if not getattr(company, f'{field}_fa', ''):
                setattr(company, f'{field}_fa', value_fa)
                setattr(company, field, value_fa)
                touched.append(f'{field}_fa')
            if not getattr(company, f'{field}_en', ''):
                setattr(company, f'{field}_en', value_en)
                touched.append(f'{field}_en')

        if touched:
            company.save()
        return touched

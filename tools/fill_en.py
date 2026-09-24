"""
ابزار توسعه: پر کردن ترجمه‌ی انگلیسی فایل locale/en.

هر msgstr خالی یا fuzzy را با ترجمه‌ی نگاشت زیر جایگزین می‌کند و پرچم fuzzy
را برمی‌دارد. اجرا:  python tools/fill_en.py
"""

import re
import sys
from pathlib import Path

PO = Path(__file__).resolve().parent.parent / 'locale' / 'en' / 'LC_MESSAGES' / 'django.po'

T = {
    # ── فهرست آیکون‌ها (پنل مدیریت) ─────────────────────────────────
    'اکسیژن (مولکول)': 'Oxygen (molecule)',
    'ماسک تنفسی': 'Breathing mask',
    'سیلندر / دستگاه قابل حمل': 'Cylinder / portable unit',
    'هواپیما': 'Aircraft',
    'کابین هواپیما': 'Aircraft cabin',
    'ارتفاع پرواز': 'Flight altitude',
    'فشارسنج / دقت اندازه‌گیری': 'Gauge / measurement accuracy',
    'ایمنی': 'Safety',
    'استاندارد / گواهی': 'Standard / certificate',
    'مهندسی طراحی': 'Design engineering',
    'سرویس و نگهداری': 'Service and maintenance',
    'تولید و مونتاژ': 'Production and assembly',
    'الکترونیک و کنترل': 'Electronics and control',
    'آزمون و آزمایشگاه': 'Testing and laboratory',
    'طراحی ماژولار': 'Modular design',
    'دقت عملکرد': 'Performance accuracy',
    'عملکرد و بهره‌وری': 'Performance and efficiency',
    'مستندسازی و کنترل کیفیت': 'Documentation and quality control',
    'وزن سبک': 'Low mass',
    'شرایط محیطی': 'Environmental conditions',
    'بازار جهانی / صادرات': 'Global market / export',
    'زنجیره تأمین و تحویل': 'Supply chain and delivery',
    'همکاری و نمایندگی': 'Partnership and distribution',
    'پشتیبانی فنی': 'Technical support',
    'کاربرد درمانی': 'Clinical application',
    'تیم و نیروی انسانی': 'Team and people',
    'محصول / بسته‌بندی': 'Product / packaging',
    'تأیید / انطباق': 'Verification / conformity',
    'نوآوری': 'Innovation',
    'موقعیت مکانی': 'Location',
    'تلفن': 'Phone',
    'ایمیل': 'Email',
    'ساعات کاری': 'Working hours',

    # ── ناوبری و چیدمان ────────────────────────────────────────────
    'اطلس': 'Atlas',
    'خانه': 'Home',
    'شرکت': 'Company',
    'فناوری‌ها': 'Technologies',
    'محصولات': 'Products',
    'صنعت‌ها': 'Industries',
    'کیفیت': 'Quality',
    'بینش': 'Insights',
    'تماس': 'Contact',
    'منو': 'Menu',
    'منوی اصلی': 'Main menu',
    'بستن منو': 'Close menu',
    'ناوبری اصلی': 'Main navigation',
    'مسیر صفحه': 'Breadcrumb',
    'رفتن به محتوای اصلی': 'Skip to main content',
    'بازگشت به بالای صفحه': 'Back to top',
    'اطلس — صفحه اصلی': 'Atlas — home',
    'نمایش سایت به %(lang)s': 'View the site in %(lang)s',
    'درخواست اطلاعات': 'Request information',
    'درخواست اطلاعات فنی': 'Request technical information',
    'مهندسی و تولید تجهیزات فنی': 'Engineering and manufacturing of technical equipment',
    'صفحه‌بندی': 'Pagination',
    'صفحه قبل': 'Previous page',
    'صفحه بعد': 'Next page',
    'Made by': 'Made by',
    'تمامی حقوق محفوظ است.': 'All rights reserved.',

    # ── صفحه اصلی ──────────────────────────────────────────────────
    'توانمندی‌های ما': 'Our capabilities',
    'کاتالوگ محصولات': 'Product catalogue',
    'حوزه‌های فناوری': 'Technology areas',
    '%(n)s حوزه فعال': '%(n)s active areas',
    '%(n)s محصول در تولید': '%(n)s products in production',
    'در حال توسعه': 'In development',
    'به‌زودی': 'Coming soon',
    'چرخه‌ی کار': 'Our cycle',
    'طراحی، ساخت، آزمون و پشتیبانی': 'Design, build, test, support',
    'مجموعه‌ی تولید': 'Production facility',
    'مجموعه‌ی مهندسی و تولید %(n)s': '%(n)s engineering and production facility',
    'مجموعه‌ی %(n)s': '%(n)s facility',
    'نقشه‌ی توانمندی': 'Capability map',
    'زنده از پنل مدیریت': 'Live from the admin',
    'حوزه‌های فناوری از پنل مدیریت اضافه می‌شوند': 'Technology areas are added from the admin panel',
    'معرفی': 'Overview',
    'مهندسی، تولید و پشتیبانی در یک مجموعه': 'Engineering, production and support under one roof',
    'درباره اطلس': 'About Atlas',
    'مهندسی و کیفیت': 'Engineering & quality',
    'فناوری': 'Technology',
    'حوزه‌هایی که در آن‌ها کار می‌کنیم': 'The areas we work in',
    'توانمندی‌های فناورانه‌ی اطلس چارچوب ثابت کار ما را می‌سازند؛ محصولات از همین حوزه‌ها بیرون می‌آیند.':
        'Atlas’s technological capabilities form the constant framework of our work; products emerge from these areas.',
    'جزئیات': 'Details',
    'همه‌ی حوزه‌های فناوری': 'All technology areas',
    'آنچه امروز تولید می‌کنیم': 'What we build today',
    'محصولات اطلس در خطوط مشخصی سازمان یافته‌اند. هر خط از یک یا چند حوزه‌ی فناوری تغذیه می‌شود.':
        'Atlas products are organised into defined lines, each drawing on one or more technology areas.',
    'کاتالوگ محصولات از پنل مدیریت تغذیه می‌شود؛ هر محصول تازه به‌طور خودکار در این بخش دیده می‌شود.':
        'The catalogue is driven from the admin panel; any new product appears in this section automatically.',
    'شاخص': 'Featured',
    'مشخصات محصول': 'Product specifications',
    'کاتالوگ در حال تکمیل است': 'The catalogue is being completed',
    'محصولات از پنل مدیریت اضافه می‌شوند و بی‌درنگ در این بخش و کاتالوگ دیده خواهند شد.':
        'Products are added from the admin panel and appear here and in the catalogue immediately.',
    'تماس با اطلس': 'Contact Atlas',
    'کاتالوگ کامل محصولات': 'Full product catalogue',
    'کجا به کار می‌آید': 'Where it is used',
    'حوزه‌هایی که فناوری‌ها و محصولات اطلس در آن‌ها کاربرد دارند.':
        'The areas where Atlas technologies and products are applied.',
    'بیشتر': 'More',
    'همه‌ی صنعت‌ها': 'All industries',
    'چرا اطلس': 'Why Atlas',
    'تمایزهایی که قابل بررسی‌اند': 'Differences you can verify',
    'چگونه کار می‌کنیم': 'How we work',
    'کیفیت در این صنعت با مدرک سنجیده می‌شود، نه با ادعا. آنچه در اختیار داریم را شفاف ارائه می‌کنیم.':
        'In this industry quality is measured by documentation, not by claims. We present what we hold, openly.',
    'استانداردها': 'Standards',
    'مستندسازی فنی': 'Technical documentation',
    'برای هر محصول، مشخصات فنی، سابقه‌ی آزمون و مدارک موجود در اختیار تیم مهندسی مشتری قرار می‌گیرد تا ارزیابی بر پایه‌ی مدرک انجام شود.':
        'For every product, specifications, test records and available documents are provided to your engineering team so evaluation rests on evidence.',
    'فرایند کیفیت': 'Quality process',
    'بازار جهانی': 'Global market',
    'آماده‌ی بازارهای بین‌المللی': 'Ready for international markets',
    'گفت‌وگو درباره صادرات': 'Discuss export',
    'صادرات': 'Export',
    'عرضه به شرکت‌ها، سازندگان و واردکنندگان خارج از ایران.':
        'Supply to companies, manufacturers and importers outside Iran.',
    'نمایندگی': 'Distribution',
    'همکاری با توزیع‌کنندگان منطقه‌ای برای پوشش بازار محلی.':
        'Working with regional distributors to cover local markets.',
    'مدارک فنی': 'Technical documents',
    'ارائه‌ی داده‌ی فنی موجود برای ارزیابی مستقل تیم مشتری.':
        'Providing available technical data for your team’s independent evaluation.',
    'تحویل': 'Delivery',
    'بسته‌بندی مناسب حمل و هماهنگی برنامه‌ی تحویل.':
        'Transport-appropriate packaging and delivery scheduling.',
    'تازه‌های اطلس': 'Latest from Atlas',
    'همه‌ی مطالب': 'All articles',
    'گفت‌وگو با اطلس': 'Talk to Atlas',
    'درباره‌ی پروژه‌ی خود با ما صحبت کنید': 'Let’s talk about your project',
    'نیاز فنی و بازار مقصد خود را برای ما بنویسید تا گزینه‌های ممکن، مشخصات و شرایط همکاری را بررسی کنیم.':
        'Tell us your technical requirement and target market, and we will review the available options, specifications and terms of cooperation.',
    'همکاری و صادرات': 'Partnership & export',

    # ── صفحه شرکت ─────────────────────────────────────────────────
    'مسیر': 'Journey',
    'نقاط عطف': 'Milestones',
    'مأموریت': 'Mission',
    'چشم‌انداز': 'Vision',
    'حوزه‌های فعالیت': 'Areas of activity',
    'توانمندی‌ها': 'Capabilities',
    'زیرساخت مهندسی و تولید': 'Engineering and production infrastructure',
    'فرایند مهندسی و کیفیت': 'Engineering and quality process',
    'تیم': 'Team',
    'افراد پشت این کار': 'The people behind the work',
    'معرفی کامل تیم': 'Meet the full team',
    'بازخورد': 'Feedback',
    'نظر همکاران و مشتریان': 'What partners and customers say',

    # ── صفحه فناوری‌ها ────────────────────────────────────────────
    'حوزه‌های فناوری و توانمندی‌های مهندسی اطلس: طراحی، ساخت، آزمون و پشتیبانی تجهیزات فنی.':
        'Atlas technology areas and engineering capabilities: design, fabrication, testing and support of technical equipment.',
    'توانمندی‌های فناورانه‌ی اطلس چارچوب ثابت کار ما را می‌سازند. محصولات از همین حوزه‌ها بیرون می‌آیند و با گسترش توانمندی‌ها، خطوط محصول تازه شکل می‌گیرند.':
        'Atlas’s technological capabilities form the constant framework of our work. Products emerge from these areas, and as the capabilities grow, new product lines follow.',
    'محصولات مرتبط': 'Related products',
    'جزئیات این حوزه': 'About this area',
    'حوزه‌های فناوری در حال تدوین است': 'Technology areas are being documented',
    'این بخش از پنل مدیریت پر می‌شود. برای گفت‌وگو درباره‌ی توانمندی‌های فنی با ما تماس بگیرید.':
        'This section is populated from the admin panel. Contact us to discuss our technical capabilities.',
    'فرایند': 'Process',
    'از نیاز تا تحویل': 'From requirement to delivery',
    'خدمات': 'Services',
    'همراهی پس از تحویل': 'Support after delivery',

    # ── صفحه صنعت‌ها ─────────────────────────────────────────────
    'صنعت‌ها و حوزه‌های کاربردی که فناوری‌ها و محصولات اطلس در آن‌ها به کار می‌آیند.':
        'The industries and application areas where Atlas technologies and products are used.',
    'صنعت‌ها و حوزه‌های کاربرد': 'Industries and applications',
    'اطلس تجهیزاتی می‌سازد که در محیط‌های پرالزام کار می‌کنند. این‌ها حوزه‌هایی است که امروز در آن‌ها فعالیم؛ با گسترش توانمندی‌ها، حوزه‌های تازه هم اضافه می‌شوند.':
        'Atlas builds equipment that operates in demanding environments. These are the areas we are active in today; as our capabilities grow, new ones will follow.',
    'این بخش در حال تکمیل است': 'This section is being completed',
    'صنعت‌ها از پنل مدیریت اضافه می‌شوند. برای گفت‌وگو درباره‌ی کاربرد در حوزه‌ی خود با ما تماس بگیرید.':
        'Industries are added from the admin panel. Contact us to discuss application in your own field.',
    'پشتوانه‌ی فنی': 'Technical foundation',
    'فناوری‌های پشت این کاربردها': 'The technologies behind these applications',

    # ── صفحه جزئیات فناوری/صنعت ─────────────────────────────────
    'مشاهده در کاتالوگ': 'View in the catalogue',
    'پرسش فنی دارید؟': 'A technical question?',
    'نیاز خود را برای ما بنویسید تا تیم مهندسی گزینه‌های ممکن را بررسی کند.':
        'Tell us your requirement and our engineering team will review the available options.',
    'ثبت درخواست': 'Submit a request',
    'دیگر حوزه‌های فناوری': 'Other technology areas',
    'دیگر صنعت‌ها': 'Other industries',

    # ── صفحه کیفیت ────────────────────────────────────────────────
    'فرایند مهندسی، کنترل کیفیت، آزمون و مستندسازی در اطلس؛ همراه با خدمات پس از تحویل.':
        'Engineering process, quality control, testing and documentation at Atlas, together with post-delivery service.',
    'کیفیت در ساخت تجهیزات فنی با مدرک سنجیده می‌شود، نه با ادعا. این‌جا فرایندی را توضیح می‌دهیم که هر واحد از آن عبور می‌کند.':
        'In technical equipment, quality is measured by documentation, not by claims. Here we set out the process every unit passes through.',
    'چه کاری را در مجموعه انجام می‌دهیم': 'What we do in-house',
    'طراحی، ساخت و آزمون در مجموعه‌ی خودمان انجام می‌شود؛ همین موضوع چرخه‌ی اصلاح را کوتاه و پاسخ‌گویی فنی را مستقیم می‌کند.':
        'Design, fabrication and testing take place in our own facility, which keeps iteration cycles short and technical accountability direct.',
    'مدارک': 'Documentation',
    'ارزیابی باید بر پایه‌ی مدرک باشد': 'Evaluation should rest on evidence',
    'الزامات تأییدیه به بازار و کاربری مقصد بستگی دارد و برای هر پروژه متفاوت است. ما مدارک فنی موجود — مشخصات، سابقه‌ی آزمون و راهنمای بهره‌برداری — را در اختیار تیم مهندسی مشتری می‌گذاریم تا مسیر لازم با هم مشخص شود.':
        'Approval requirements depend on the destination market and use case, and differ from project to project. We provide the technical documentation we hold — specifications, test records and operating guides — to your engineering team so the required path can be mapped out together.',
    'هیچ ادعایی درباره‌ی تأییدیه‌ای که در اختیار نداریم مطرح نمی‌کنیم.':
        'We make no claim about any approval we do not hold.',
    'درخواست مدارک فنی': 'Request technical documents',
    'مشخصات فنی': 'Technical specifications',
    'داده‌ی عملکردی هر محصول به‌صورت مکتوب ارائه می‌شود.':
        'Performance data for each product is provided in writing.',
    'سابقه‌ی آزمون': 'Test records',
    'نتیجه‌ی آزمون در پرونده‌ی هر شماره سری ثبت می‌شود.':
        'Test results are recorded in the file of each serial number.',
    'راهنمای بهره‌برداری': 'Operating guide',
    'دستور کار و راهنمای نگهداری همراه محصول تحویل می‌شود.':
        'An operating procedure and maintenance guide are delivered with the product.',
    'پاسخ فنی': 'Technical answers',
    'پرسش‌های تیم مهندسی مشتری مستقیم پاسخ داده می‌شود.':
        'Questions from your engineering team are answered directly.',
    'پرسش‌های پرتکرار': 'Frequently asked',
    'سؤالات متداول': 'Frequently asked questions',
    # ── کاتالوگ محصولات ───────────────────────────────────────────
    'کاتالوگ محصولات اطلس — تجهیزات فنی طراحی و ساخته‌شده در مجموعه‌ی خودمان، دسته‌بندی‌شده بر پایه‌ی خط محصول، حوزه‌ی فناوری و صنعت.':
        'The Atlas product catalogue — technical equipment designed and built in our own facility, organised by product line, technology area and industry.',
    'هر محصول از یک یا چند حوزه‌ی فناوری اطلس بیرون آمده است. برای یافتن سریع‌تر، بر پایه‌ی خط محصول، فناوری یا صنعت فیلتر کنید.':
        'Every product comes out of one or more Atlas technology areas. Filter by product line, technology or industry to find what you need.',
    'خط محصول': 'Product line',
    'صنعت': 'Industry',
    'همه': 'All',
    'جست‌وجو': 'Search',
    'جست‌وجوی محصول': 'Search products',
    'نام یا کد محصول': 'Product name or code',
    '%(counter)s محصول': '%(counter)s products',
    'حذف فیلترها': 'Clear filters',
    'محصولی با این فیلترها پیدا نشد': 'No products match these filters',
    'فیلترها را تغییر دهید، یا نیاز خود را برای ما بنویسید تا گزینه‌های ممکن را بررسی کنیم.':
        'Adjust the filters, or tell us your requirement and we will review the available options.',
    'محصولات از پنل مدیریت اضافه می‌شوند و بی‌درنگ در این کاتالوگ دیده خواهند شد.':
        'Products are added from the admin panel and appear in this catalogue immediately.',
    'طرح نیاز فنی': 'Describe your requirement',

    # ── صفحه محصول ────────────────────────────────────────────────
    'بخش‌های این صفحه': 'Sections on this page',
    'ویژگی‌ها': 'Features',
    'مشخصات': 'Specifications',
    'کاربردها': 'Applications',
    'استعلام': 'Enquiry',
    'ویژگی‌های کلیدی': 'Key features',
    'یادداشت فنی': 'Technical note',
    'مدارک و کاتالوگ': 'Documents and catalogue',
    'استعلام محصول': 'Product enquiry',
    'برای دریافت مشخصات کامل، شرایط تحویل و گزینه‌های پیکربندی، درخواست خود را ثبت کنید.':
        'Submit a request for the full specification, delivery terms and configuration options.',
    'ایمیل فروش': 'Sales email',
    'بر پایه‌ی این فناوری‌ها': 'Built on these technologies',
    'همچنین ببینید': 'See also',

    # ── تیم ───────────────────────────────────────────────────────
    'تیم اطلس': 'The Atlas team',
    'تیم مهندسی، تولید و پشتیبانی اطلس.': 'The Atlas engineering, production and support team.',
    'مهندسان طراحی، تولید و پشتیبانی که هر محصول را از ایده تا تحویل همراهی می‌کنند.':
        'The design, production and support engineers who take every product from concept to delivery.',
    'معرفی تیم در حال تکمیل است': 'Team profiles are being completed',
    'اعضای تیم از پنل مدیریت اضافه می‌شوند.': 'Team members are added from the admin panel.',
    'ایمیل %(n)s': 'Email %(n)s',
    'لینکدین %(n)s': '%(n)s on LinkedIn',

    # ── بینش / اخبار ──────────────────────────────────────────────
    'بینش و اخبار': 'Insights & news',
    'اخبار شرکت، یادداشت‌های فنی و مطالب مهندسی اطلس.':
        'Company news, technical notes and engineering articles from Atlas.',
    'یادداشت‌های فنی، رویدادهای شرکت و مطالبی درباره‌ی کاری که انجام می‌دهیم.':
        'Technical notes, company events and writing about the work we do.',
    'موضوع': 'Topic',
    'ادامه مطلب': 'Read more',
    'هنوز مطلبی منتشر نشده': 'Nothing published yet',
    'یادداشت‌های فنی و اخبار شرکت در این بخش منتشر می‌شوند.':
        'Technical notes and company news will be published in this section.',
    'بازگشت به فهرست مطالب': 'Back to all articles',
    'همچنین بخوانید': 'Also read',
    'مطالب مرتبط': 'Related articles',

    # ── تماس ──────────────────────────────────────────────────────
    'تماس بازرگانی و فنی با اطلس: درخواست اطلاعات، استعلام، همکاری و صادرات.':
        'Commercial and technical contact with Atlas: information requests, enquiries, partnership and export.',
    'با اطلس صحبت کنید': 'Talk to Atlas',
    'نیاز فنی، بازار مقصد یا موضوع همکاری خود را بنویسید. کارشناسان ما در کمتر از یک روز کاری پاسخ می‌دهند.':
        'Tell us your technical requirement, target market or partnership interest. Our specialists respond within one business day.',
    'اطلاعات فنی': 'Technical information',
    'مشخصات، مدارک و داده‌ی عملکردی محصول.': 'Specifications, documents and product performance data.',
    'استعلام و خرید': 'Enquiry and purchase',
    'قیمت، شرایط تحویل و برنامه‌ی تأمین.': 'Pricing, delivery terms and supply schedule.',
    'نمایندگی، توزیع و بازارهای بین‌المللی.': 'Distribution, resale and international markets.',
    'اطلاعات تماس': 'Contact details',
    'تماس بازرگانی': 'Commercial contact',
    'فناوری و محصول': 'Technology & products',
    'نشانی': 'Address',
    'کد پستی': 'Postal code',
    'فکس': 'Fax',
    'ارسال درخواست': 'Send request',
    'فیلدهای ستاره‌دار الزامی هستند.': 'Fields marked with an asterisk are required.',
    'این فیلد را خالی بگذارید': 'Leave this field empty',
    'اطلاعات شما محفوظ است و فقط برای پاسخ‌گویی استفاده می‌شود.':
        'Your information stays private and is used only to reply to you.',
    'نقشه موقعیت شرکت': 'Company location map',

    # ── فرم تماس (contact/forms.py) ───────────────────────────────
    'نام و نام خانوادگی': 'Full name',
    'شماره تماس': 'Phone number',
    'نام سازمان': 'Organisation',
    'موضوع درخواست': 'Request type',
    'متن پیام': 'Message',
    'محصول مرتبط': 'Related product',
    'نام و نام خانوادگی خود را وارد کنید': 'Enter your full name',
    'example@email.com': 'example@email.com',
    'اختیاری': 'Optional',
    'موضوع پیام شما': 'Subject of your message',
    'پیام خود را بنویسید...': 'Write your message…',
    '— انتخاب کنید (اختیاری) —': '— Select (optional) —',
    'ارسال فرم ناموفق بود.': 'The form could not be submitted.',
    'متن پیام باید حداقل ۱۰ کاراکتر باشد.': 'The message must be at least 10 characters long.',
    'استعلام قیمت و خرید': 'Pricing and purchase enquiry',
    'پرسش فنی': 'Technical question',
    'پشتیبانی و خدمات پس از فروش': 'Support and after-sales service',
    'سایر موارد': 'Other',
    'پیام شما با موفقیت ارسال شد. به‌زودی با شما تماس خواهیم گرفت.':
        'Your message has been sent. We will get back to you shortly.',
    'لطفاً خطاهای فرم را بررسی کنید.': 'Please review the errors in the form.',
    'استعلام درباره %(product)s': 'Enquiry about %(product)s',
    'ارسال پیام': 'Send message',
    'موضوع': 'Subject',

    # ── صفحات خطا ─────────────────────────────────────────────────
    'صفحه پیدا نشد': 'Page not found',
    'این صفحه پیدا نشد': 'We couldn’t find that page',
    'ممکن است نشانی تغییر کرده یا صفحه حذف شده باشد. از مسیرهای زیر ادامه دهید.':
        'The address may have changed or the page may have been removed. Continue from the links below.',
    'صفحه اصلی': 'Home',
    'خطای سرور': 'Server error',
    'خطایی در سرور رخ داد': 'Something went wrong on our side',
    'مشکل به تیم فنی گزارش شد. لطفاً چند لحظه بعد دوباره تلاش کنید.':
        'The issue has been reported to our technical team. Please try again in a moment.',
    'بازگشت به صفحه اصلی': 'Back to home',
}


def escape(v):
    return v.replace('\\', '\\\\').replace('"', '\\"')


def literal(block):
    return ''.join(m.replace('\\"', '"') for m in re.findall(r'"(.*)"', block))


def main():
    text = PO.read_text(encoding='utf-8')
    blocks = text.split('\n\n')
    out, filled, unknown = [], 0, []

    for block in blocks:
        if 'msgid ' not in block or block.lstrip().startswith('msgid ""\nmsgstr ""'):
            out.append(block)
            continue

        m = re.search(r'^msgid ((?:".*"\n?)+)', block, re.M)
        if not m:
            out.append(block)
            continue

        key = literal(m.group(1))
        is_fuzzy = '#, fuzzy' in block
        is_empty = bool(re.search(r'^msgstr ""$', block, re.M))
        plural = 'msgid_plural' in block

        if not (is_fuzzy or is_empty):
            out.append(block)
            continue

        value = T.get(key)
        if value is None:
            if key:
                unknown.append(key)
            out.append(block)
            continue

        # پرچم fuzzy و کامنت‌های #| را حذف کن
        lines = [l for l in block.split('\n') if not l.startswith('#|')]
        lines = [l for l in lines if l.strip() != '#, fuzzy']
        lines = [re.sub(r'^#, fuzzy, ', '#, ', l) for l in lines]
        lines = [re.sub(r'^#, (.*), fuzzy$', r'#, \1', l) for l in lines]
        block = '\n'.join(lines)

        if plural:
            block = re.sub(r'^msgstr\[0\] (?:".*"\n?)+', f'msgstr[0] "{escape(value)}"\n', block, count=1, flags=re.M)
            block = re.sub(r'^msgstr\[1\] (?:".*"\n?)+', f'msgstr[1] "{escape(value)}"\n', block, count=1, flags=re.M)
        else:
            block = re.sub(r'^msgstr (?:".*"\n?)+', f'msgstr "{escape(value)}"\n', block, count=1, flags=re.M)

        out.append(block.rstrip('\n'))
        filled += 1

    PO.write_text('\n\n'.join(out), encoding='utf-8')
    print(f'filled: {filled}')
    if unknown:
        print(f'still missing ({len(unknown)}):')
        for k in unknown:
            print('   ', k)
    return 0 if not unknown else 1


if __name__ == '__main__':
    sys.exit(main())


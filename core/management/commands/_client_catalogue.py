"""
داده‌های برگرفته از کاتالوگ‌های کارفرما (پوشه‌ی «کاتالوگ» در فایل شماره‌ی ۲):

* ATLAS Rigging Catalogue (۴۲ صفحه) — مشخصات و ویژگی‌های اقلام لیفتینگ، ریگینگ و مهار.
* Buoyancy Modules Catalogue (۴ صفحه) — بویه‌ها و مدول‌های شناوری ساخت اطلس.
* General Catalogue — خدمات (از جمله پیش‌بینی وضع هوای دریایی).

اعداد و استانداردها عیناً از کاتالوگ‌ها آمده‌اند؛ متن‌ها کوتاه و فنی نگه داشته شده‌اند.
"""

# ─────────────────────────────────────────────── شعار برند (متن کارفرما)
SLOGAN = (
    'جایی که خطا گران است، ما با اطمینان عمل می‌کنیم؛ چون خود را شریک پروژه‌ی شما می‌دانیم.',
    'Where mistakes are expensive, we act with confidence — because we see ourselves as a partner in your project.',
)

# ─────────────────────────────────────────────── خدمت چهارم (کاتالوگ عمومی)
WEATHER_SERVICE = (
    'خدمات پیش‌بینی وضع هوای دریایی',
    'Marine weather forecast services',
    'ارائه‌ی خدمات هواشناسی دریایی از طریق شرکت‌های بزرگی چون Fugro، Met Consultancy و '
    'Global Meteocean؛ به‌موقع، دقیق و با قیمت مناسب برای برنامه‌ریزی عملیات فراساحل.',
    'Marine weather forecasting through leading providers such as Fugro, Met Consultancy and '
    'Global Meteocean — timely, accurate and fairly priced, for planning offshore operations.',
    'icon-thermometer',
)

# ─────────────────────────────────────────────── خط محصول تازه: بویه‌ها و شناورسازها
BUOYANCY_CATEGORY = (
    'buoyancy-modules',
    'بویه‌ها و شناورسازها (ساخت اطلس)', 'Buoys & Buoyancy Modules (Atlas-made)',
    'بویه‌ها و مدول‌های شناوری فومی که در اطلس طراحی و ساخته می‌شوند؛ اندازه، طرح، وزن و '
    'میزان شناوری متناسب با نیاز پروژه قابل تنظیم است.',
    'Foam buoys and buoyancy modules designed and manufactured by Atlas. Size, design, weight '
    'and buoyancy can be adjusted to each project’s requirements.',
    'icon-layers',
)

BUOYANCY_TECH = ('metal-polymer-manufacturing', 'quality-control-testing', 'documentation-traceability')
BUOYANCY_IND = ('offshore-oil-gas', 'marine-shipping', 'heavy-lift-pipeline')

# (نامک، نام فا، نام en، کد مدل، توضیح کوتاه فا، توضیح کوتاه en، شاخص)
NEW_PRODUCTS = [
    (
        'pipeline-buoyancy-module', 'buoyancy-modules',
        'مدول شناوری خط لوله', 'Pipeline Buoyancy Module', 'AT-PLBT',
        'مدول شناوری فومی برای خطوط لوله‌ی ۸ تا ۶۰ اینچ؛ شناوری خالص ۵۰۰ تا ۴۰۰۰ کیلوگرم.',
        'Foam buoyancy module for 8"–60" pipelines; net buoyancy 500–4,000 kg.',
        True, BUOYANCY_TECH, BUOYANCY_IND,
    ),
    (
        'bundle-buoyancy-module', 'buoyancy-modules',
        'مدول شناوری باندل لوله', 'Bundle Buoyancy Module', 'AT-DBL',
        'مدول شناوری برای باندل لوله‌های ۸ تا ۶۰ اینچ؛ شناوری خالص ۵۰ تا ۱۰۰۰ کیلوگرم.',
        'Buoyancy module for 8"–60" pipe bundles; net buoyancy 50–1,000 kg.',
        False, BUOYANCY_TECH, BUOYANCY_IND,
    ),
    (
        'small-medium-buoys', 'buoyancy-modules',
        'بویه‌های کوچک و متوسط', 'Small & Medium Buoys', 'AT-SB1 ~ AT-SB6',
        'بویه‌های کروی، دوکی و استوانه‌ای با قطر ۲۰۰ تا ۱۱۵۰ میلی‌متر و شناوری خالص تا ۱۰۲۰ کیلوگرم.',
        'Spherical, spindle and cylindrical buoys, 200–1,150 mm in diameter, with net buoyancy up to 1,020 kg.',
        False, BUOYANCY_TECH, ('offshore-oil-gas', 'marine-shipping'),
    ),
    (
        'mooring-buoys', 'buoyancy-modules',
        'بویه‌های مهاربندی', 'Mooring Buoys', 'AT-MB1 ~ AT-MB3',
        'بویه‌های Pendant، Pick-up و Chain-through با شناوری خالص تا ۱۷۹۵ کیلوگرم.',
        'Pendant, pick-up and chain-through buoys with net buoyancy up to 1,795 kg.',
        False, BUOYANCY_TECH, ('offshore-oil-gas', 'marine-shipping'),
    ),
    (
        'anchors', 'lifting-rigging-equipment',
        'لنگر (Anchors)', 'Anchors', '',
        'لنگرهای پرظرفیت Delta و Danforth (HHP) برای مهار شناورها و سازه‌های دریایی.',
        'Delta and Danforth high-holding-power (HHP) anchors for mooring vessels and offshore structures.',
        False, ('industrial-sourcing', 'metal-polymer-manufacturing', 'quality-control-testing'),
        ('offshore-oil-gas', 'marine-shipping'),
    ),
]

# نام تازه‌ی اسلینگ‌ها — پوشه‌ی کارفرما «اسلینگ و گرومت و تسمه» است.
RENAMES = {
    'slings-grommets': ('اسلینگ، گرومت و تسمه (Sling, Grommet & Webbing)', 'Slings, Grommets & Webbing Slings'),
}


def spec(label_fa, label_en, value_fa, value_en, unit_fa='', unit_en='', highlight=False, group=('', '')):
    return {
        'label': (label_fa, label_en), 'value': (value_fa, value_en), 'unit': (unit_fa, unit_en),
        'highlight': highlight, 'group': group,
    }


def feature(title_fa, title_en, desc_fa='', desc_en=''):
    return {'title': (title_fa, title_en), 'description': (desc_fa, desc_en)}


def buoy(model, dia, length, nb, weight):
    g = (model, model)
    return [
        spec('قطر', 'Diameter', dia, dia, 'میلی‌متر', 'mm', group=g),
        spec('طول', 'Length', length, length, 'میلی‌متر', 'mm', group=g),
        spec('شناوری خالص', 'Net buoyancy', nb, nb, 'کیلوگرم', 'kg', group=g),
        spec('وزن', 'Weight', weight, weight, 'کیلوگرم', 'kg', group=g),
    ]


def mooring(model, pendant, pickup, chain):
    g = (model, model)
    return [
        spec('Pendant — وزن / شناوری خالص', 'Pendant — weight / net buoyancy', pendant, pendant, 'کیلوگرم', 'kg', group=g),
        spec('Pick-up — وزن / شناوری خالص', 'Pick-up — weight / net buoyancy', pickup, pickup, 'کیلوگرم', 'kg', group=g),
        spec('Chain-through — وزن / شناوری خالص', 'Chain-through — weight / net buoyancy', chain, chain, 'کیلوگرم', 'kg', group=g),
    ]


CUSTOM_NOTE = (
    'اندازه، طرح، وزن و میزان شناوری بر اساس نیاز پروژه قابل تنظیم است.',
    'Size, design, weight and buoyancy can be adjusted to your requirements.',
)
NETT_NOTE = (
    'شناوری خالص بدون قطعات فلزی و متعلقات محاسبه شده است.',
    'Net buoyancy is given without metallic parts and accessories.',
)
RIGGING_DOC = ('کاتالوگ لیفتینگ و ریگینگ اطلس', 'Atlas lifting & rigging catalogue', 'docs/atlas-rigging-catalogue.pdf')
BUOYANCY_DOC = ('کاتالوگ بویه‌ها و شناورسازها', 'Buoys & buoyancy modules catalogue', 'docs/atlas-buoyancy-catalogue.pdf')
GENERAL_DOC = ('کاتالوگ عمومی اطلس', 'Atlas general catalogue', 'docs/atlas-general-catalogue.pdf')

# ─────────────────────────────────────────────── جزئیات محصولات
# detail: پاراگراف تکمیلی توضیحات · specs · features · docs
PRODUCT_DETAILS = {
    'shackles': {
        'detail': (
            'انواع شکل Bolt Type، Screw Pin، Wide Body، Wide Mouth و Dee/Bow؛ فولاد آلیاژی فورج‌شده '
            'با پین آلیاژی، کوئنچ و تمپر، با پوشش گالوانیزه‌ی گرم یا رنگی. محصولات الزامات استاندارد '
            'ASME B30.26 را برآورده می‌کنند و در صورت درخواست با گواهی تست بار و گواهی‌های ABS، DNV '
            'یا Lloyd’s تحویل داده می‌شوند.',
            'Bolt-type, screw-pin, wide-body, wide-mouth and Dee/Bow shackles — forged alloy steel with '
            'alloy pins, quenched and tempered, hot-dip galvanised or painted. Products meet ASME B30.26 '
            'and can be supplied proof-tested with ABS, DNV or Lloyd’s certification on request.',
        ),
        'specs': [
            spec('ظرفیت کاری (WLL)', 'Working load limit', '۱/۳ تا ۱۰۰۰', '1/3 – 1,000', 'تن', 't', True),
            spec('استاندارد', 'Standard', 'ASME B30.26 · RR-C-271', 'ASME B30.26 · RR-C-271', highlight=True),
            spec('جنس', 'Material', 'فولاد آلیاژی فورج، کوئنچ و تمپر', 'Forged alloy steel, quenched & tempered', highlight=True),
            spec('پوشش', 'Finish', 'گالوانیزه‌ی گرم / رنگی', 'Hot-dip galvanised / painted'),
            spec('گواهی', 'Certification', 'ABS، DNV، Lloyd’s (در صورت درخواست)', 'ABS, DNV, Lloyd’s (on request)', highlight=True),
            spec('ضریب ایمنی', 'Safety factor', '۶ برابر WLL (MBL)', '6 × WLL (MBL)'),
        ],
        'features': [
            feature('درج دائمی WLL', 'WLL permanently marked', 'ظرفیت کاری روی بدنه‌ی هر شکل حک شده است.', 'The working load limit is permanently shown on every shackle.'),
            feature('مقاومت ضربه‌ی DNV', 'DNV impact rated', 'قابلیت برآورده کردن الزام ضربه‌ی ۴۲ ژول در ‎-۲۰°C.', 'Can meet DNV impact requirements of 42 J at −20 °C.'),
            feature('تست غیرمخرب و ردیابی', 'NDT and traceability', 'شکل‌های ۸۵ تن و بالاتر با تست غیرمخرب و شماره‌سریال پین و بدنه.', 'Shackles of 85 t and above available non-destructively tested with serialised pin and bow.'),
        ],
        'docs': [RIGGING_DOC],
    },
    'hooks': {
        'detail': (
            'هوک‌های بار با قفل ایمنی و هوک‌های سنگین جرثقیل‌های دریایی، همراه با حلقه‌ی اصلی '
            '(Master Link) و حلقه‌های اتصال از فولاد آلیاژی کوئنچ و تمپر که هر کدام با ۲٫۵ برابر '
            'ظرفیت کاری تست و گواهی می‌شوند.',
            'Load hooks with safety latches and heavy crane-barge hooks, together with master links and '
            'connecting links in quenched-and-tempered alloy steel, each individually proof-tested at '
            '2.5 × the working load limit with certification.',
        ),
        'specs': [
            spec('حلقه‌ی اتصال — جنس', 'Links — material', 'فولاد آلیاژی کوئنچ و تمپر', 'Alloy steel, quenched & tempered', highlight=True),
            spec('تست بار', 'Proof test', '۲٫۵ برابر WLL، با گواهی', '2.5 × WLL, certified', highlight=True),
            spec('ضریب طراحی', 'Design factor', '۴:۱ زنجیر · ۵:۱ سیم‌بکسل', '4:1 chain · 5:1 wire rope', highlight=True),
            spec('ردیابی', 'Traceability', 'کد شناسایی محصول (PIC) روی هر قطعه', 'Product identification code (PIC) on each part'),
        ],
        'features': [
            feature('قفل ایمنی', 'Safety latch', 'جلوگیری از خروج ناخواسته‌ی بار از هوک.', 'Prevents the load from slipping off the hook.'),
            feature('هوک‌های سنگین فراساحل', 'Heavy offshore hooks', 'برای جرثقیل‌ها و بارج‌های سنگین پروژه‌های دریایی.', 'For heavy cranes and crane barges on marine projects.'),
        ],
        'docs': [RIGGING_DOC],
    },
    'blocks-sheaves': {
        'detail': (
            'بلاک‌های Snatch و قرقره‌های صنعتی با هوک‌های آلیاژی فورج‌شده؛ قابلیت باز شدن بدنه برای '
            'قرار دادن سیم در حالی که بلاک آویزان است، با بوش برنزی یا بلبرینگ غلتکی. اطلس انواع '
            'قرقره‌ی صنعتی را نیز می‌سازد.',
            'Snatch blocks and industrial sheaves with forged alloy hooks. The opening side allows rope '
            'to be inserted while the block is suspended; bronze bushings or roller bearings available. '
            'Atlas also manufactures industrial blocks.',
        ),
        'specs': [
            spec('قطر قرقره', 'Sheave diameter', '۷۶ تا ۴۵۷', '76 – 457', 'میلی‌متر', 'mm', True),
            spec('بار نهایی', 'Ultimate load', '۴ برابر WLL', '4 × WLL', highlight=True),
            spec('یاتاقان', 'Bearing', 'بوش برنزی / بلبرینگ غلتکی', 'Bronze bushing / roller bearing', highlight=True),
            spec('اتصال', 'Fitting', 'هوک یا شکل (قابل تعویض)', 'Hook or shackle (interchangeable)'),
        ],
        'features': [
            feature('باز شدن بدنه', 'Opening side plate', 'قرار دادن سیم بدون نیاز به باز کردن بار.', 'Insert rope without unloading the block.'),
            feature('ساخت داخلی', 'Made by Atlas', 'قرقره‌های صنعتی در مجموعه‌ی اطلس ساخته می‌شوند.', 'Industrial blocks are manufactured by Atlas.'),
        ],
        'docs': [RIGGING_DOC],
    },
    'slings-grommets': {
        'detail': (
            'اسلینگ‌ها و گرومت‌های Cable Laid برای بالابری سنگین مطابق IMCA M179، EN 13414-3 یا PM20؛ '
            'اسلینگ‌های چندرشته‌ای Gator-Max و Gator-Flex؛ اسلینگ سیمی تا قطر ۷۱ میلی‌متر؛ تسمه‌های '
            'باربرداری پلی‌استر مطابق EN 1492-1 (ضریب ایمنی ۷:۱) یا BS 3481 (۶:۱)؛ و طناب‌های نایلونی، '
            'پلی‌پروپیلن و مانیلا (BS 2052). تسمه‌ی باربرداری در اطلس ساخته می‌شود.',
            'Heavy-lift cable-laid slings and grommets to IMCA M179, EN 13414-3 or PM20; Gator-Max and '
            'Gator-Flex multi-part slings; wire rope slings up to 71 mm; polyester webbing slings to '
            'EN 1492-1 (7:1) or BS 3481 (6:1); and nylon, polypropylene and manila ropes (BS 2052). '
            'Lifting belts are manufactured by Atlas.',
        ),
        'specs': [
            spec('اسلینگ Cable Laid', 'Cable-laid slings', 'IMCA M179 · EN 13414-3 · PM20', 'IMCA M179 · EN 13414-3 · PM20', highlight=True),
            spec('تسمه‌ی پلی‌استر', 'Polyester webbing', 'EN 1492-1 (۷:۱) · BS 3481 (۶:۱)', 'EN 1492-1 (7:1) · BS 3481 (6:1)', highlight=True),
            spec('اسلینگ سیمی', 'Wire rope slings', 'تا قطر ۷۱', 'up to 71', 'میلی‌متر', 'mm', True),
            spec('طناب', 'Ropes', 'نایلون، پلی‌پروپیلن، مانیلا (BS 2052)', 'Nylon, polypropylene, manila (BS 2052)'),
        ],
        'features': [
            feature('اسلینگ‌های Gator', 'Gator slings', 'بیش از ۹۰٪ بازده؛ استحکام کامل حتی روی پین‌های کوچک (D/d = 1:1).', 'Over 90% efficiency; full strength even on small pins (D/d = 1:1).'),
            feature('چشمی‌های محافظت‌شده', 'Protected eyes', 'روکش پلی‌استر یا چرمی برای عمر بیشتر تسمه.', 'Polyester or leather eye protection for longer sling life.'),
            feature('ساخت سفارشی', 'Custom slings', 'اسلینگ‌های ویژه و تور بار مطابق نیاز پروژه.', 'Special-purpose slings and cargo nets to project requirements.'),
        ],
        'docs': [RIGGING_DOC],
    },
    'wire-rope': {
        'detail': (
            'سیم‌بکسل‌های قطور شش‌رشته‌ای Neptune برای جرثقیل‌ها و صنعت نفت (کلاس 6x36 IWRC و بالاتر، '
            'رشته‌ی فشرده‌ی CMP)، خطوط Riser Tensioner و Drilling Line، طناب‌های لنگر و وینچ، و سیم‌بکسل '
            'استنلس‌استیل 7x19، 7x7 و 1x19؛ همراه با سوکت‌ها و اتصالات با بازده ۱۰۰٪.',
            'Neptune large-diameter six-strand crane and oil-industry ropes (class 6x36 IWRC and above, '
            'compact strand CMP), marine riser tensioner and drilling lines, anchor and winch ropes, and '
            '7x19, 7x7 and 1x19 stainless steel rope — with sockets and terminations of 100% efficiency.',
        ),
        'specs': [
            spec('ساختار', 'Construction', '6x36 IWRC · 6x41 · 6x49 · CMP', '6x36 IWRC · 6x41 · 6x49 · CMP', highlight=True),
            spec('حفاظت', 'Protection', 'گالوانیزه یا ALUMAR', 'Galvanised or ALUMAR', highlight=True),
            spec('استنلس‌استیل', 'Stainless steel', '7x19 · 7x7 · 1x19', '7x19 · 7x7 · 1x19'),
            spec('بازده اتصالات', 'Termination efficiency', '۱۰۰٪', '100%', highlight=True),
        ],
        'features': [
            feature('خطوط حفاری و Riser', 'Drilling and riser lines', 'ساختارهای انعطاف‌پذیر با Lang’s lay برای عمر خستگی بیشتر.', 'Flexible Lang’s-lay constructions for optimum fatigue life.'),
            feature('رشته‌ی فشرده (CMP)', 'Compact strand (CMP)', 'سطح تماس بیشتر و سایش کمتر قرقره و شیار.', 'Greater contact area and reduced sheave and groove wear.'),
        ],
        'docs': [RIGGING_DOC],
    },
    'winches': {
        'detail': (
            'وینچ‌های برقی دستی و چندمنظوره‌ی دریایی برای مهاربندی چهارنقطه‌ای و عملیات Anchor Handling '
            'و یدک‌کشی، با امکان سامانه‌ی پایش و کنترل کشش و جمع‌کن خودکار؛ همچنین کپستان‌های '
            'یکپارچه یا مستقل برای جمع‌آوری ایمن طناب‌های مهار. ساخت سفارشی مطابق مشخصات مشتری ممکن است.',
            'Manual and multi-purpose electric marine winches for 4-point mooring, anchor handling and '
            'towing, with optional tension monitoring and auto-spool control; plus integrated or '
            'freestanding capstans for safe hauling of mooring lines. Custom builds to customer specification.',
        ),
        'specs': [
            spec('نوع', 'Type', 'برقی · دستی · چندمنظوره', 'Electric · manual · multi-purpose', highlight=True),
            spec('کاربرد', 'Application', 'مهار چهارنقطه‌ای · Anchor Handling · یدک‌کشی', '4-point mooring · anchor handling · towing', highlight=True),
            spec('گزینه‌ها', 'Options', 'پایش کشش · جمع‌کن خودکار', 'Tension monitoring · auto-spool', highlight=True),
        ],
        'features': [
            feature('کپستان', 'Capstans', 'با ترمز، استارتر، پدال و چرخش دوطرفه.', 'With brake, motor starter, footswitch and reversible rotation.'),
            feature('ساخت سفارشی', 'Custom manufacture', 'طراحی و ساخت مطابق مشخصات پروژه.', 'Designed and built to project specifications.'),
        ],
        'docs': [RIGGING_DOC],
    },
    'turnbuckles-swivels': {
        'detail': (
            'ترن‌باکل‌ها و پیچ‌های ریگینگ گالوانیزه‌ی گرم، تست‌شده و دارای گواهی مطابق US Fed FF-T-791 و '
            'ASTM F1145-92، همراه با سوییول‌های بدنه‌بسته برای جلوگیری از پیچش بار.',
            'Hot-dip galvanised turnbuckles and rigging screws, tested and certified to US Fed FF-T-791 '
            'and ASTM F1145-92, together with closed-body swivels that prevent load twisting.',
        ),
        'specs': [
            spec('استاندارد', 'Standard', 'US Fed FF-T-791 · ASTM F1145-92', 'US Fed FF-T-791 · ASTM F1145-92', highlight=True),
            spec('پوشش', 'Finish', 'گالوانیزه‌ی گرم', 'Hot-dip galvanised', highlight=True),
            spec('گواهی', 'Certification', 'تست‌شده و دارای گواهی', 'Tested & certified', highlight=True),
        ],
        'features': [],
        'docs': [RIGGING_DOC],
    },
    'anchors': {
        'detail': (
            'لنگرهای پرظرفیت Delta (HHP) و لنگرهای Danforth فولاد ریختگی برای مهاربندی شناورها، بارج‌ها '
            'و سازه‌های دریایی. اطلس ساخت لنگر را نیز انجام می‌دهد.',
            'Delta high-holding-power (HHP) anchors and cast-steel Danforth HHP anchors for mooring vessels, '
            'barges and offshore structures. Atlas also manufactures anchors.',
        ),
        'specs': [
            spec('انواع', 'Types', 'Delta HHP · Danforth HHP', 'Delta HHP · Danforth HHP', highlight=True),
            spec('جنس Danforth', 'Danforth material', 'فولاد ریختگی', 'Cast steel', highlight=True),
            spec('ساخت داخلی', 'Manufacturing', 'ساخت اطلس (در صورت نیاز)', 'Made by Atlas (on request)', highlight=True),
        ],
        'features': [],
        'docs': [RIGGING_DOC],
    },
    'pipeline-buoyancy-module': {
        'detail': (
            'مدول شناوری فومی که روی خط لوله نصب می‌شود تا وزن مؤثر لوله در آب کاهش یابد و نصب خطوط لوله‌ی '
            'دریایی ساده‌تر شود.',
            'A foam buoyancy module clamped onto the pipeline to reduce its effective weight in water and '
            'simplify subsea pipeline installation.',
        ),
        'specs': [
            spec('قطر خط لوله', 'Pipeline diameter', '۸ تا ۶۰', '8 – 60', 'اینچ', 'in', True),
            spec('شناوری خالص', 'Net buoyancy', '۵۰۰ تا ۴۰۰۰', '500 – 4,000', 'کیلوگرم', 'kg', True),
            spec('وزن', 'Weight', '۱۰۰ تا ۶۰۰', '100 – 600', 'کیلوگرم', 'kg', True),
        ],
        'features': [feature('قابل سفارشی‌سازی', 'Customisable', *CUSTOM_NOTE)],
        'docs': [BUOYANCY_DOC],
    },
    'bundle-buoyancy-module': {
        'detail': (
            'مدول شناوری دوتکه که چند لوله را در قالب یک باندل در بر می‌گیرد و شناوری لازم را برای '
            'نصب و جابه‌جایی آن فراهم می‌کند.',
            'A two-piece buoyancy module that clamps several pipes into a single bundle and provides the '
            'buoyancy needed for installation and handling.',
        ),
        'specs': [
            spec('قطر خط لوله', 'Pipeline diameter', '۸ تا ۶۰', '8 – 60', 'اینچ', 'in', True),
            spec('شناوری خالص', 'Net buoyancy', '۵۰ تا ۱۰۰۰', '50 – 1,000', 'کیلوگرم', 'kg', True),
            spec('وزن', 'Weight', '۱۰۰ تا ۵۰۰', '100 – 500', 'کیلوگرم', 'kg', True),
        ],
        'features': [feature('قابل سفارشی‌سازی', 'Customisable', *CUSTOM_NOTE)],
        'docs': [BUOYANCY_DOC],
    },
    'small-medium-buoys': {
        'detail': (
            'شش مدل بویه‌ی کوچک و متوسط در فرم‌های کروی، دوکی و استوانه‌ای برای نشانه‌گذاری، شناورسازی '
            'و مهار سبک.',
            'Six models of small and medium buoys in spherical, spindle and cylindrical forms, for marking, '
            'flotation and light mooring.',
        ),
        'specs': (
            buoy('AT-SB1', '۲۰۰–۶۲۰', '۲۰۰–۱۰۸۰', '۳٫۳–۲۴۰', '۰٫۹–۲۶')
            + buoy('AT-SB2', '۴۰۰', '۳۰۰–۱۶۰۰', '۱۹–۳۷', '۳٫۳–۶٫۶')
            + buoy('AT-SB3', '۵۰۰', '۵۰۰–۲۰۰۰', '۷۰–۳۰۰', '۲۸–۱۰۰')
            + buoy('AT-SB4', '۶۰۰', '۴۰۰–۲۳۰۰', '۹۸–۴۸۴', '۱۴–۶۶')
            + buoy('AT-SB5', '۶۰۰–۶۷۰', '۵۲۰–۱۱۰۰', '۴۹–۳۲۷', '۹٫۵–۳۳')
            + buoy('AT-SB6', '۷۰۰–۱۱۵۰', '۴۴۰–۱۱۵۰', '۱۳۷–۱۰۲۰', '۱۷–۱۳۰')
        ),
        'highlight': [
            spec('قطر', 'Diameter', '۲۰۰ تا ۱۱۵۰', '200 – 1,150', 'میلی‌متر', 'mm', True),
            spec('شناوری خالص', 'Net buoyancy', '۳٫۳ تا ۱۰۲۰', '3.3 – 1,020', 'کیلوگرم', 'kg', True),
            spec('تعداد مدل', 'Models', '۶ مدل', '6 models', highlight=True),
        ],
        'features': [feature('شناوری خالص', 'Net buoyancy', *NETT_NOTE)],
        'docs': [BUOYANCY_DOC],
    },
    'mooring-buoys': {
        'detail': (
            'سه مدل بویه‌ی مهاربندی، هر کدام در سه نوع Pendant، Pick-up و Chain-through؛ وزن و شناوری '
            'با احتساب قطعات فلزی ذکر شده است.',
            'Three models of mooring buoys, each in pendant, pick-up and chain-through types; weight and '
            'buoyancy include metallic parts.',
        ),
        'specs': (
            mooring('AT-MB1', '۱۱۰–۶۰۰ / ۲۰۵–۱۷۷۵', '۱۰۰–۵۸۰ / ۲۱۵–۱۷۹۵', '۱۱۰–۶۰۰ / ۲۰۵–۱۷۷۵')
            + mooring('AT-MB2', '۱۸۰–۵۲۰ / ۴۵۰–۱۴۰۰', '۱۶۰–۵۰۰ / ۴۷۰–۱۴۲۰', '۱۸۰–۵۲۰ / ۴۵۰–۱۴۰۰')
            + mooring('AT-MB3', '۱۸۰–۵۲۰ / ۴۵۰–۱۴۰۰', '۱۶۰–۵۰۰ / ۴۷۰–۱۴۲۰', '۱۸۰–۵۲۰ / ۴۵۰–۱۴۰۰')
        ),
        'highlight': [
            spec('شناوری خالص', 'Net buoyancy', 'تا ۱۷۹۵', 'up to 1,795', 'کیلوگرم', 'kg', True),
            spec('انواع', 'Types', 'Pendant · Pick-up · Chain-through', 'Pendant · Pick-up · Chain-through', highlight=True),
            spec('تعداد مدل', 'Models', '۳ مدل', '3 models', highlight=True),
        ],
        'features': [],
        'docs': [BUOYANCY_DOC],
    },
    'heavy-marine-equipment': {'docs': [GENERAL_DOC]},
    'hydraulic-mechanical-components': {'docs': [GENERAL_DOC]},
    'marine-platform-spare-parts': {
        'detail': (
            'تأمین قطعات یدکی تجهیزات دریایی و سکوهای نفتی، آهن‌آلات و شیت پایل.',
            'Supply of spare parts for marine equipment and oil platforms, steel material and sheet piles.',
        ),
        'docs': [GENERAL_DOC],
    },
}

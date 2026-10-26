"""
تصویر پس‌زمینه‌ی سربرگ صفحات داخلی.

عکس‌ها از Unsplash (مجوز رایگان Unsplash License؛ استفاده‌ی تجاری بدون نیاز به
ذکر منبع) انتخاب شده‌اند. فایل محلی هر عکس در static/images/heads/<کلید>.jpg
نگهداری می‌شود و با دستور زیر یک‌بار دانلود می‌شود:

    python manage.py fetch_header_images

تا وقتی فایل محلی وجود نداشته باشد، همان عکس مستقیماً از CDN آن‌اسپلش
نمایش داده می‌شود تا سربرگ هیچ‌وقت خالی نماند.
"""

# کلید صفحه: (شناسه‌ی عکس در images.unsplash.com، صفحه‌ی عکس در Unsplash، توضیح)
HEAD_IMAGES = {
    'about': (
        '1749073668528-38ab64575f5d',
        'https://unsplash.com/photos/3J2FB7BItdA',
        'سکوی نفتی فراساحل و شناور پشتیبانی',
    ),
    'industries': (
        '1758902064778-c5c68c7e8f82',
        'https://unsplash.com/photos/0eqs4wjebyc',
        'شناور جرثقیل‌دار نصب سنگین در دریا',
    ),
    'technologies': (
        '1787039467622-ddec5c24320c',
        'https://unsplash.com/photos/O6YIDLs4AZE',
        'کارگاه ماشین‌کاری CNC',
    ),
    'quality': (
        '1747999827332-163aa33cd597',
        'https://unsplash.com/photos/EA7QL-GJWRM',
        'اندازه‌گیری دقیق قطعه‌ی فلزی',
    ),
    'team': (
        '1759922378222-47ad736a174d',
        'https://unsplash.com/photos/nlXv_JCfSHc',
        'تیم مهندسی با کلاه ایمنی',
    ),
    'news': (
        '1759272840538-ae4b07214c71',
        'https://unsplash.com/photos/fT4SwA83jH4',
        'بندر کانتینری و حمل بین‌المللی',
    ),
    'contact': (
        '1703355685722-2996b01483be',
        'https://unsplash.com/photos/ov_ctAopIoI',
        'اتاق جلسه',
    ),
    'products': (
        '1776062157210-c777e94aacd4',
        'https://unsplash.com/photos/-7-JXRf_V5A',
        'قلاب جرثقیل و سیم‌بکسل',
    ),
}

STATIC_DIR = 'images/heads'
DOWNLOAD_WIDTH = 2000


def cdn_url(photo_id, width=DOWNLOAD_WIDTH, quality=70):
    return (
        f'https://images.unsplash.com/photo-{photo_id}'
        f'?w={width}&q={quality}&fm=jpg&fit=crop&auto=format'
    )


def static_path(key):
    return f'{STATIC_DIR}/{key}.jpg'

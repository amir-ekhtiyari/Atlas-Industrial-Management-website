from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .constants import DEFAULT_ICON, ICON_CHOICES
from .images import OptimizedImagesMixin


class OrderedContentQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class OrderedContent(models.Model):
    """
    پایه‌ی مشترک همه‌ی بلوک‌های محتوایی سایت: عنوان، توضیح، آیکون،
    ترتیب نمایش و کلید فعال/غیرفعال. هیچ جدولی برای این کلاس ساخته نمی‌شود.
    """
    title = models.CharField(max_length=150, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیح")
    icon = models.CharField(
        max_length=40,
        choices=ICON_CHOICES,
        default=DEFAULT_ICON,
        verbose_name="آیکون",
        help_text="آیکون برداری از فهرست آماده؛ نیازی به آپلود تصویر نیست.",
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    objects = OrderedContentQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class PageContent(OrderedContent):
    """
    بلوک محتوایی که صفحه‌ی اختصاصی خودش را هم دارد (حوزه‌ی فناوری، صنعت).

    نامک به‌صورت خودکار از عنوان ساخته می‌شود، اما مدیر سایت می‌تواند آن را
    دستی هم تعیین کند. `summary` برای کارت‌ها و `body` برای صفحه‌ی کامل است.
    """
    slug = models.SlugField(
        max_length=120, unique=True, allow_unicode=True, blank=True,
        verbose_name="نامک (URL)",
        help_text="اگر خالی بماند، از عنوان ساخته می‌شود.",
    )
    body = models.TextField(
        blank=True, verbose_name="متن کامل صفحه",
        help_text="اگر پر شود، صفحه‌ی اختصاصی این مورد در سایت ساخته می‌شود.",
    )
    meta_description = models.CharField(
        max_length=300, blank=True, verbose_name="توضیح متا",
        help_text="اگر خالی بماند، از توضیح کوتاه استفاده می‌شود.",
    )

    class Meta(OrderedContent.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:110] or 'item'
            self.slug = base
        super().save(*args, **kwargs)

    @property
    def has_page(self):
        """صفحه‌ی اختصاصی فقط وقتی معنا دارد که متن کاملی نوشته شده باشد."""
        return bool(self.body)

    @property
    def display_meta_description(self):
        return self.meta_description or self.description



class CompanyInfo(OptimizedImagesMixin, models.Model):
    """
    اطلاعات عمومی شرکت. این مدل به‌صورت Singleton طراحی شده،
    یعنی همیشه فقط یک رکورد از آن در دیتابیس وجود خواهد داشت.
    """
    OPTIMIZED_IMAGE_FIELDS = ('hero_image', 'about_image', 'og_image')

    name = models.CharField(max_length=150, verbose_name="نام شرکت")
    logo = models.ImageField(
        upload_to='company/', blank=True, null=True, verbose_name="لوگو",
        help_text="اگر خالی بماند، نشان برداری داخلی اطلس در هدر و فوتر استفاده می‌شود.",
    )
    tagline = models.CharField(max_length=250, blank=True, verbose_name="شعار شرکت")
    hero_text = models.TextField(verbose_name="متن معرفی صفحه اصلی")
    about_text = models.TextField(verbose_name="متن درباره ما")

    # --- صفحه اصلی ---
    hero_title = models.CharField(
        max_length=200, blank=True, verbose_name="تیتر اصلی صفحه اول",
        help_text="اگر خالی بماند، نام شرکت نمایش داده می‌شود.",
    )
    hero_image = models.ImageField(
        upload_to='company/', blank=True, null=True, verbose_name="تصویر صفحه اول",
        help_text="تصویر افقی و باکیفیت از محصول یا خط تولید. در صورت خالی بودن، لوگو نمایش داده می‌شود.",
    )
    intro_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان بخش معرفی شرکت")
    intro_text = models.TextField(blank=True, verbose_name="متن بخش معرفی شرکت")
    about_image = models.ImageField(
        upload_to='company/', blank=True, null=True, verbose_name="تصویر صفحه درباره ما",
    )
    mission_text = models.TextField(blank=True, verbose_name="مأموریت شرکت")
    vision_text = models.TextField(blank=True, verbose_name="چشم‌انداز شرکت")

    # --- بازار جهانی و صادرات ---
    global_title = models.CharField(
        max_length=200, blank=True, verbose_name="عنوان بخش بازار جهانی",
    )
    global_text = models.TextField(
        blank=True, verbose_name="متن بخش بازار جهانی",
        help_text="موقعیت شرکت برای صادرات و همکاری بین‌المللی. از ادعاهای تأییدنشده پرهیز کنید.",
    )

    # --- فراخوان اقدام (CTA) ---
    cta_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان بخش فراخوان")
    cta_text = models.CharField(max_length=300, blank=True, verbose_name="متن بخش فراخوان")

    # --- تماس ---
    address = models.CharField(max_length=300, verbose_name="آدرس")
    phone = models.CharField(max_length=20, verbose_name="تلفن")
    secondary_phone = models.CharField(max_length=20, blank=True, verbose_name="تلفن دوم")
    fax = models.CharField(max_length=20, blank=True, verbose_name="فکس")
    email = models.EmailField(verbose_name="ایمیل")
    sales_email = models.EmailField(blank=True, verbose_name="ایمیل فروش")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="کد پستی")
    working_hours = models.CharField(max_length=150, blank=True, verbose_name="ساعات کاری")
    map_embed_url = models.URLField(
        blank=True, verbose_name="لینک نقشه (embed)",
        help_text="آدرس iframe نقشه گوگل یا نشان. در صفحه تماس نمایش داده می‌شود.",
    )

    # --- شبکه‌های اجتماعی ---
    instagram_url = models.URLField(blank=True, verbose_name="لینک اینستاگرام")
    linkedin_url = models.URLField(blank=True, verbose_name="لینک لینکدین")
    telegram_url = models.URLField(blank=True, verbose_name="لینک تلگرام")
    whatsapp_url = models.URLField(blank=True, verbose_name="لینک واتس‌اپ")
    youtube_url = models.URLField(blank=True, verbose_name="لینک یوتیوب")

    # --- سئو ---
    meta_description = models.CharField(
        max_length=300, blank=True, verbose_name="توضیح متا (پیش‌فرض سایت)",
        help_text="حدود ۱۵۰ کاراکتر؛ در نتایج گوگل نمایش داده می‌شود.",
    )
    og_image = models.ImageField(
        upload_to='company/', blank=True, null=True, verbose_name="تصویر اشتراک‌گذاری",
        help_text="تصویری که هنگام اشتراک لینک سایت در شبکه‌های اجتماعی نمایش داده می‌شود.",
    )

    # --- اطلاعات تکمیلی ---
    notification_email = models.EmailField(
        blank=True, verbose_name="ایمیل دریافت پیام‌های فرم تماس",
        help_text="اگر خالی بماند، پیام‌ها فقط در پنل مدیریت ذخیره می‌شوند.",
    )

    class Meta:
        verbose_name = "اطلاعات شرکت"
        verbose_name_plural = "اطلاعات شرکت"

    def __str__(self):
        return self.name

    def clean(self):
        # جلوگیری از ساخت رکورد دوم
        if not self.pk and CompanyInfo.objects.exists():
            raise ValidationError("فقط یک رکورد اطلاعات شرکت مجاز است. رکورد موجود را ویرایش کنید.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.first()

    @property
    def display_hero_title(self):
        return self.hero_title or self.name

    @property
    def has_social_links(self):
        return any([
            self.instagram_url, self.linkedin_url, self.telegram_url,
            self.whatsapp_url, self.youtube_url,
        ])

    @property
    def social_links(self):
        """فهرست آماده‌ی شبکه‌های اجتماعی پرشده، برای رندر تمیز در قالب‌ها."""
        candidates = (
            ('icon-linkedin', 'LinkedIn', self.linkedin_url),
            ('icon-instagram', 'Instagram', self.instagram_url),
            ('icon-telegram', 'Telegram', self.telegram_url),
            ('icon-whatsapp', 'WhatsApp', self.whatsapp_url),
            ('icon-youtube', 'YouTube', self.youtube_url),
        )
        return [
            {'icon': icon, 'label': label, 'url': url}
            for icon, label, url in candidates if url
        ]


class Technology(PageContent, OptimizedImagesMixin):
    """
    یک حوزه‌ی فناوری/توانمندی اطلس — سطحی بالاتر از محصول.

    هر فناوری می‌تواند به چند محصول متصل باشد (`Product.technologies`) و اگر
    متن کاملی برای آن نوشته شود، صفحه‌ی اختصاصی خودش را می‌گیرد. این مدل
    ستون فقرات ساختار «شرکت‌محور» سایت است: محصول‌ها می‌آیند و می‌روند،
    حوزه‌های فناوری چارچوب ثابت می‌سازند.
    """
    OPTIMIZED_IMAGE_FIELDS = ('image',)

    image = models.ImageField(
        upload_to='technologies/', blank=True, null=True, verbose_name="تصویر (اختیاری)",
        help_text="در کارت و بالای صفحه‌ی این فناوری استفاده می‌شود.",
    )

    class Meta(PageContent.Meta):
        verbose_name = "حوزه فناوری"
        verbose_name_plural = "حوزه‌های فناوری"

    def get_absolute_url(self):
        return reverse('core:technology_detail', kwargs={'slug': self.slug})


class Industry(PageContent, OptimizedImagesMixin):
    """
    صنعت/حوزه‌ی کاربرد که اطلس در آن فعال است.

    جانشین مدل قبلی `Application` است و برخلاف آن، صفحه‌ی اختصاصی و ارتباط
    با محصولات دارد؛ بنابراین افزودن یک صنعت تازه (مثلاً ریلی یا دریایی)
    نیازی به تغییر کد ندارد.
    """
    OPTIMIZED_IMAGE_FIELDS = ('image',)

    image = models.ImageField(
        upload_to='industries/', blank=True, null=True, verbose_name="تصویر (اختیاری)",
    )

    class Meta(PageContent.Meta):
        verbose_name = "صنعت / حوزه کاربرد"
        verbose_name_plural = "صنعت‌ها و حوزه‌های کاربرد"

    def get_absolute_url(self):
        return reverse('core:industry_detail', kwargs={'slug': self.slug})


class Service(OrderedContent):
    """خدمات شرکت (مشاوره، تحویل، آموزش، پشتیبانی و ...)."""
    image = models.ImageField(
        upload_to='services/', blank=True, null=True, verbose_name="تصویر (اختیاری)",
        help_text="در صورت آپلود، جایگزین آیکون می‌شود.",
    )

    class Meta(OrderedContent.Meta):
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"


class Advantage(OrderedContent):
    """«چرا اطلس» — تمایزهای شرکت."""

    class Meta(OrderedContent.Meta):
        verbose_name = "تمایز"
        verbose_name_plural = "تمایزها (چرا اطلس)"


class Capability(OrderedContent):
    """توانمندی‌های مهندسی، تولید و کنترل کیفیت."""

    class Meta(OrderedContent.Meta):
        verbose_name = "توانمندی"
        verbose_name_plural = "توانمندی‌های مهندسی و تولید"


class Certification(OrderedContent):
    """استانداردها، مجوزها و گواهی‌نامه‌ها."""
    issuer = models.CharField(max_length=150, blank=True, verbose_name="مرجع صدور")
    image = models.ImageField(
        upload_to='certifications/', blank=True, null=True, verbose_name="تصویر گواهی (اختیاری)",
    )

    class Meta(OrderedContent.Meta):
        verbose_name = "استاندارد / گواهی‌نامه"
        verbose_name_plural = "استانداردها و گواهی‌نامه‌ها"


class Statistic(models.Model):
    """آمار و دستاوردها؛ اعداد کوتاه برای ایجاد اعتماد در صفحه اصلی."""
    value = models.CharField(
        max_length=20, verbose_name="عدد",
        help_text="مثال: ۱۵ یا 250 — فقط عدد را وارد کنید.",
    )
    suffix = models.CharField(
        max_length=20, blank=True, verbose_name="پسوند",
        help_text="مثال: +، سال، دستگاه",
    )
    label = models.CharField(max_length=120, verbose_name="عنوان")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    objects = OrderedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "آمار / دستاورد"
        verbose_name_plural = "آمار و دستاوردها"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.value}{self.suffix} — {self.label}"


class Milestone(models.Model):
    """نقاط عطف شرکت؛ در صفحه درباره ما به‌صورت خط زمانی نمایش داده می‌شود."""
    year = models.CharField(max_length=10, verbose_name="سال")
    title = models.CharField(max_length=150, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیح")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    objects = OrderedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "نقطه عطف"
        verbose_name_plural = "نقاط عطف (خط زمانی)"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.year} — {self.title}"


class FAQ(models.Model):
    """پرسش‌های پرتکرار؛ در صفحه تماس نمایش داده می‌شود."""
    question = models.CharField(max_length=250, verbose_name="پرسش")
    answer = models.TextField(verbose_name="پاسخ")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    objects = OrderedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "پرسش پرتکرار"
        verbose_name_plural = "پرسش‌های پرتکرار"
        ordering = ['order', 'id']

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    """نظر مشتریان و همکاران تجاری."""
    quote = models.TextField(verbose_name="متن نظر")
    author = models.CharField(max_length=150, verbose_name="نام گوینده")
    role = models.CharField(max_length=150, blank=True, verbose_name="سمت / سازمان")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    objects = OrderedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "نظر مشتری"
        verbose_name_plural = "نظرات مشتریان"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.author} — {self.quote[:40]}"


class ProcessStep(models.Model):
    """مراحل فرایند همکاری/تولید؛ برای بخش «فرایند کار ما»."""
    step_number = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        verbose_name="شماره مرحله",
    )
    title = models.CharField(max_length=150, verbose_name="عنوان مرحله")
    description = models.TextField(blank=True, verbose_name="توضیح")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    objects = OrderedContentQuerySet.as_manager()

    class Meta:
        verbose_name = "مرحله فرایند"
        verbose_name_plural = "فرایند همکاری"
        ordering = ['step_number', 'id']

    def __str__(self):
        return f"{self.step_number}. {self.title}"

# products/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.constants import DEFAULT_ICON, ICON_CHOICES
from core.images import OptimizedImagesMixin


class Category(models.Model):
    """
    خط محصول. ساختار سایت حول دسته‌بندی‌ها چیده شده، پس افزودن یک خط محصول
    تازه (بدون ارتباط با خطوط فعلی) هیچ تغییری در کد لازم ندارد.
    """
    name = models.CharField(max_length=100, verbose_name="نام خط محصول")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="نامک (URL)")
    description = models.TextField(blank=True, verbose_name="توضیح خط محصول")
    icon = models.CharField(
        max_length=40, choices=ICON_CHOICES, default=DEFAULT_ICON, verbose_name="آیکون",
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "خط محصول"
        verbose_name_plural = "خطوط محصول"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('products:list')}?line={self.slug}"


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_related(self):
        """
        برای فهرست محصولات: خط محصول را join می‌کند تا در حلقه‌ی قالب،
        هر کارت یک کوئری اضافه نزند (رفع N+1).
        """
        return self.select_related('category')


class Product(OptimizedImagesMixin, models.Model):
    OPTIMIZED_IMAGE_FIELDS = ('image',)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="خط محصول",
    )
    technologies = models.ManyToManyField(
        'core.Technology',
        blank=True,
        related_name='products',
        verbose_name="حوزه‌های فناوری",
        help_text="فناوری‌هایی که این محصول بر آن‌ها تکیه دارد.",
    )
    industries = models.ManyToManyField(
        'core.Industry',
        blank=True,
        related_name='products',
        verbose_name="صنعت‌ها",
        help_text="صنعت‌هایی که این محصول در آن‌ها کاربرد دارد.",
    )
    name = models.CharField(max_length=200, verbose_name="نام محصول")
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name="نامک (URL)")
    model_code = models.CharField(
        max_length=60, blank=True, verbose_name="کد / مدل محصول",
    )
    tagline = models.CharField(
        max_length=160, blank=True, verbose_name="عنوان فرعی",
        help_text="یک سطر کوتاه که جایگاه محصول را مشخص می‌کند.",
    )
    short_description = models.CharField(max_length=300, verbose_name="توضیح کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل")
    image = models.ImageField(
        upload_to='products/', blank=True, null=True, verbose_name="تصویر محصول",
        help_text="اگر خالی بماند، یک قاب طرح‌دار با کد/نام محصول نمایش داده می‌شود.",
    )
    specifications = models.TextField(
        blank=True, verbose_name="یادداشت فنی (متن آزاد)",
        help_text="برای جدول مشخصات، از بخش «مشخصات فنی» پایین همین صفحه استفاده کنید. "
                  "این فیلد برای توضیحات تکمیلی است.",
    )

    # --- سئو ---
    meta_description = models.CharField(
        max_length=300, blank=True, verbose_name="توضیح متا",
        help_text="اگر خالی بماند، از توضیح کوتاه استفاده می‌شود.",
    )

    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")
    is_featured = models.BooleanField(
        default=False, db_index=True, verbose_name="محصول شاخص",
        help_text="محصولات شاخص در صفحه اصلی نمایش داده می‌شوند.",
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['is_active', 'order'], name='product_active_order_idx'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)[:200] or 'product'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def display_meta_description(self):
        return self.meta_description or self.short_description


class ProductImage(OptimizedImagesMixin, models.Model):
    """گالری تصاویر هر محصول."""
    OPTIMIZED_IMAGE_FIELDS = ('image',)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول",
    )
    image = models.ImageField(upload_to='products/gallery/', verbose_name="تصویر")
    caption = models.CharField(
        max_length=200, blank=True, verbose_name="توضیح تصویر",
        help_text="برای دسترس‌پذیری و سئو مفید است (متن alt).",
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "گالری تصاویر"
        ordering = ['order', 'id']

    def __str__(self):
        return self.caption or f"{self.product.name} — {self.pk}"

    @property
    def alt_text(self):
        return self.caption or self.product.name


class ProductSpecification(models.Model):
    """یک ردیف از جدول مشخصات فنی محصول."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='specs', verbose_name="محصول",
    )
    group = models.CharField(
        max_length=100, blank=True, verbose_name="گروه",
        help_text="مثال: عملکرد، ابعاد، محیط کار. ردیف‌های هم‌گروه کنار هم نمایش داده می‌شوند.",
    )
    label = models.CharField(max_length=150, verbose_name="عنوان مشخصه")
    value = models.CharField(max_length=250, verbose_name="مقدار")
    unit = models.CharField(max_length=40, blank=True, verbose_name="واحد")
    is_highlight = models.BooleanField(
        default=False, verbose_name="نمایش در نوار شاخص",
        help_text="مشخصه‌های علامت‌خورده بالای صفحه‌ی محصول به‌عنوان سنجه‌های کلیدی دیده می‌شوند.",
    )
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "مشخصه فنی"
        verbose_name_plural = "مشخصات فنی"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.label}: {self.value}"

    @property
    def display_value(self):
        return f"{self.value} {self.unit}".strip()


class ProductFeature(models.Model):
    """ویژگی‌ها و مزیت‌های کلیدی محصول."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='features', verbose_name="محصول",
    )
    title = models.CharField(max_length=150, verbose_name="عنوان ویژگی")
    description = models.TextField(blank=True, verbose_name="توضیح")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصول"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ProductApplication(models.Model):
    """کاربردهای محصول."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='applications', verbose_name="محصول",
    )
    title = models.CharField(max_length=150, verbose_name="عنوان کاربرد")
    description = models.TextField(blank=True, verbose_name="توضیح")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "کاربرد محصول"
        verbose_name_plural = "کاربردهای محصول"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ProductDocument(models.Model):
    """کاتالوگ و مدارک فنی قابل دانلود."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='documents', verbose_name="محصول",
    )
    title = models.CharField(max_length=150, verbose_name="عنوان مدرک")
    file = models.FileField(upload_to='products/documents/', verbose_name="فایل")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "مدرک فنی"
        verbose_name_plural = "مدارک و کاتالوگ‌ها"
        ordering = ['order', 'id']

    def __str__(self):
        return self.title

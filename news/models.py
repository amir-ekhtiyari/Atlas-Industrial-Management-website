# news/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core.images import OptimizedImagesMixin


class PostCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, allow_unicode=True, verbose_name="نامک (URL)")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "دسته‌بندی خبر"
        verbose_name_plural = "دسته‌بندی‌های اخبار"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('news:list')}?category={self.slug}"


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, published_at__lte=timezone.now())

    def with_related(self):
        return self.select_related('category')


class Post(OptimizedImagesMixin, models.Model):
    """خبر، مقاله یا یادداشت فنی شرکت."""
    OPTIMIZED_IMAGE_FIELDS = ('cover',)

    category = models.ForeignKey(
        PostCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name="دسته‌بندی",
    )
    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name="نامک (URL)")
    summary = models.CharField(max_length=300, verbose_name="خلاصه")
    body = models.TextField(verbose_name="متن کامل")
    cover = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="تصویر شاخص")

    meta_description = models.CharField(
        max_length=300, blank=True, verbose_name="توضیح متا",
        help_text="اگر خالی بماند، از خلاصه استفاده می‌شود.",
    )

    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    published_at = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="تاریخ انتشار")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = "خبر / مقاله"
        verbose_name_plural = "اخبار و مقالات"
        ordering = ['-published_at', '-id']
        indexes = [
            models.Index(fields=['is_published', '-published_at'], name='post_pub_date_idx'),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)[:200] or 'post'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    @property
    def display_meta_description(self):
        return self.meta_description or self.summary

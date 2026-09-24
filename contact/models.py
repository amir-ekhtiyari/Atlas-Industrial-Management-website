# contact/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'جدید'
        IN_PROGRESS = 'in_progress', 'در حال بررسی'
        ANSWERED = 'answered', 'پاسخ داده شده'
        ARCHIVED = 'archived', 'بایگانی'

    class Topic(models.TextChoices):
        SALES = 'sales', _('استعلام قیمت و خرید')
        TECHNICAL = 'technical', _('پرسش فنی')
        SUPPORT = 'support', _('پشتیبانی و خدمات پس از فروش')
        PARTNERSHIP = 'partnership', _('همکاری و نمایندگی')
        OTHER = 'other', _('سایر موارد')

    name = models.CharField(max_length=150, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    company = models.CharField(max_length=150, blank=True, verbose_name="نام سازمان")
    topic = models.CharField(
        max_length=20, choices=Topic.choices, default=Topic.SALES, verbose_name="موضوع درخواست",
    )
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="متن پیام")

    related_product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name="محصول مرتبط",
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW,
        db_index=True, verbose_name="وضعیت",
    )
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    admin_note = models.TextField(blank=True, verbose_name="یادداشت داخلی")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="تاریخ ارسال")

    class Meta:
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read', '-created_at'], name='contact_unread_idx'),
        ]

    def __str__(self):
        return f"{self.name} - {self.subject}"

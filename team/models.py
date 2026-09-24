# team/models.py
from django.db import models

from core.images import OptimizedImagesMixin


class TeamMember(OptimizedImagesMixin, models.Model):
    OPTIMIZED_IMAGE_FIELDS = ('photo',)

    full_name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی")
    position = models.CharField(max_length=150, verbose_name="سمت")
    photo = models.ImageField(
        upload_to='team/', blank=True, null=True, verbose_name="عکس پرسنلی",
        help_text="اگر خالی بماند، حروف اول نام در یک قاب ساده نمایش داده می‌شود.",
    )
    bio = models.TextField(blank=True, verbose_name="توضیح کوتاه")
    email = models.EmailField(blank=True, verbose_name="ایمیل کاری")
    linkedin_url = models.URLField(blank=True, verbose_name="لینک لینکدین")
    order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="نمایش در سایت")

    class Meta:
        verbose_name = "عضو تیم"
        verbose_name_plural = "اعضای تیم"
        ordering = ['order', 'id']

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        """حروف اول نام، برای جایگزینی عکس نداشته."""
        parts = [p for p in (self.full_name or '').split() if p]
        return ''.join(p[0] for p in parts[:2]).upper()

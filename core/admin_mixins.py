"""
ابزارهای مشترک پنل مدیریت.

`AtlasTranslationAdmin` پایه‌ی همه‌ی ModelAdmin‌های دارای فیلد ترجمه است و
فایل‌های ظاهری/رفتاری پنل (سوییچ زبان محتوا) را همراه خود می‌آورد.
"""

from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

PLACEHOLDER = '—'

ADMIN_CSS = {'all': ('atlas-admin/admin.css',)}
ADMIN_JS = ('atlas-admin/admin.js',)


def render_image_preview(image, height=56, max_width=120):
    """پیش‌نمایش کوچک برای ستون‌های فهرست."""
    if not image:
        return PLACEHOLDER
    return format_html(
        '<img src="{}" alt="" loading="lazy" style="height:{}px;width:auto;max-width:{}px;'
        'border-radius:6px;border:1px solid #d8dee6;object-fit:cover;background:#fff;">',
        image.url, height, max_width,
    )


def render_image_preview_large(image, max_height=220):
    """پیش‌نمایش بزرگ‌تر برای صفحه‌ی ویرایش."""
    if not image:
        return PLACEHOLDER
    return format_html(
        '<img src="{}" alt="" loading="lazy" style="max-height:{}px;max-width:100%;'
        'border-radius:8px;border:1px solid #d8dee6;background:#fff;">',
        image.url, max_height,
    )


class AtlasAdminMedia:
    class Media:
        css = ADMIN_CSS
        js = ADMIN_JS


class AtlasModelAdmin(AtlasAdminMedia, admin.ModelAdmin):
    """ModelAdmin پروژه برای مدل‌های بدون ترجمه."""


class AtlasTranslationAdmin(AtlasAdminMedia, TranslationAdmin):
    """
    ModelAdmin پروژه برای مدل‌های چندزبانه. فیلدهای هر زبان با نوار
    «زبان محتوا» بالای فرم قابل فیلتر شدن است (پیاده‌سازی در admin.js).
    """


class ImagePreviewMixin:
    """
    نام فیلد تصویر را در `preview_field` تعیین کنید؛ سپس می‌توانید
    `image_preview` را در list_display یا readonly_fields به کار ببرید.
    """

    preview_field = 'image'
    preview_height = 56

    @admin.display(description='پیش‌نمایش')
    def image_preview(self, obj):
        return render_image_preview(getattr(obj, self.preview_field, None), self.preview_height)

    @admin.display(description='پیش‌نمایش')
    def image_preview_large(self, obj):
        return render_image_preview_large(getattr(obj, self.preview_field, None))


class OrderedContentAdmin(AtlasTranslationAdmin):
    """
    پیکربندی مشترک برای همه‌ی بلوک‌های محتوایی مبتنی بر `core.models.OrderedContent`.
    """

    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('order', 'id')
    list_per_page = 30

    fieldsets = (
        ('محتوا', {'fields': ('title', 'description', 'icon')}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )


__all__ = [
    'AtlasModelAdmin',
    'AtlasTranslationAdmin',
    'ImagePreviewMixin',
    'OrderedContentAdmin',
    'TranslationTabularInline',
    'render_image_preview',
    'render_image_preview_large',
]

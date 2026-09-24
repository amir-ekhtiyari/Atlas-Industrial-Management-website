from django.contrib import admin

from core.admin_mixins import AtlasTranslationAdmin, ImagePreviewMixin
from .models import Post, PostCategory


@admin.register(PostCategory)
class PostCategoryAdmin(AtlasTranslationAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('order', 'name')


@admin.register(Post)
class PostAdmin(ImagePreviewMixin, AtlasTranslationAdmin):
    preview_field = 'cover'
    list_display = ('image_preview', 'title', 'category', 'is_published', 'published_at')
    list_display_links = ('image_preview', 'title')
    list_filter = ('is_published', 'category', 'published_at')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    list_select_related = ('category',)
    readonly_fields = ('created_at', 'updated_at', 'cover_preview')
    date_hierarchy = 'published_at'
    save_on_top = True
    ordering = ('-published_at',)

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'slug', 'category'),
        }),
        ('تصویر شاخص', {
            'fields': ('cover', 'cover_preview'),
        }),
        ('محتوا', {
            'fields': ('summary', 'body'),
        }),
        ('سئو', {
            'fields': ('meta_description',),
            'classes': ('collapse',),
        }),
        ('انتشار', {
            'fields': ('is_published', 'published_at', 'created_at', 'updated_at'),
        }),
    )

    @admin.display(description='پیش‌نمایش تصویر شاخص')
    def cover_preview(self, obj):
        return self.image_preview_large(obj)

    @admin.action(description='انتشار موارد انتخاب‌شده')
    def publish(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} مطلب منتشر شد.')

    @admin.action(description='لغو انتشار موارد انتخاب‌شده')
    def unpublish(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} مطلب از حالت انتشار خارج شد.')

    actions = ['publish', 'unpublish']

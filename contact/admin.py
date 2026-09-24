from django.contrib import admin
from django.utils.html import format_html

from core.admin_mixins import AtlasModelAdmin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(AtlasModelAdmin):
    list_display = (
        'status_badge', 'name', 'subject', 'topic', 'email',
        'related_product', 'is_read', 'created_at',
    )
    list_display_links = ('name', 'subject')
    list_filter = ('status', 'is_read', 'topic', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company', 'subject', 'message')
    readonly_fields = (
        'name', 'email', 'phone', 'company', 'topic',
        'subject', 'message', 'related_product', 'created_at',
    )
    list_editable = ('is_read',)
    list_select_related = ('related_product',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 30

    fieldsets = (
        ('فرستنده', {'fields': ('name', 'email', 'phone', 'company')}),
        ('پیام', {'fields': ('topic', 'subject', 'message', 'related_product', 'created_at')}),
        ('پیگیری', {'fields': ('status', 'is_read', 'admin_note')}),
    )

    STATUS_COLORS = {
        ContactMessage.Status.NEW: '#B3261E',
        ContactMessage.Status.IN_PROGRESS: '#A66A00',
        ContactMessage.Status.ANSWERED: '#0E7A67',
        ContactMessage.Status.ARCHIVED: '#5A6B7C',
    }

    @admin.display(description='وضعیت', ordering='status')
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#5A6B7C')
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
            'background:{}1a;color:{};font-weight:600;font-size:12px;white-space:nowrap;">{}</span>',
            color, color, obj.get_status_display(),
        )

    def has_add_permission(self, request):
        # پیام‌ها فقط از طریق فرم سایت ایجاد می‌شوند.
        return False

    @admin.action(description='علامت‌گذاری به‌عنوان خوانده‌شده')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} پیام خوانده‌شده علامت خورد.')

    @admin.action(description='تغییر وضعیت به «در حال بررسی»')
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.IN_PROGRESS, is_read=True)
        self.message_user(request, f'{updated} پیام در حال بررسی علامت خورد.')

    @admin.action(description='تغییر وضعیت به «پاسخ داده شده»')
    def mark_answered(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.ANSWERED, is_read=True)
        self.message_user(request, f'{updated} پیام پاسخ‌داده‌شده علامت خورد.')

    @admin.action(description='بایگانی کردن')
    def mark_archived(self, request, queryset):
        updated = queryset.update(status=ContactMessage.Status.ARCHIVED, is_read=True)
        self.message_user(request, f'{updated} پیام بایگانی شد.')

    actions = ['mark_as_read', 'mark_in_progress', 'mark_answered', 'mark_archived']

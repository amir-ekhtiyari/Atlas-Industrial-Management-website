from django.contrib import admin

from core.admin_mixins import AtlasTranslationAdmin, ImagePreviewMixin
from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(ImagePreviewMixin, AtlasTranslationAdmin):
    preview_field = 'photo'
    list_display = ('image_preview', 'full_name', 'position', 'order', 'is_active')
    list_display_links = ('image_preview', 'full_name')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('full_name', 'position', 'bio')
    ordering = ('order', 'id')
    readonly_fields = ('photo_preview',)

    fieldsets = (
        ('هویت', {'fields': ('full_name', 'position')}),
        ('عکس', {'fields': ('photo', 'photo_preview')}),
        ('معرفی', {'fields': ('bio',)}),
        ('راه‌های ارتباطی', {'fields': ('email', 'linkedin_url'), 'classes': ('collapse',)}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )

    @admin.display(description='پیش‌نمایش عکس')
    def photo_preview(self, obj):
        return self.image_preview_large(obj)

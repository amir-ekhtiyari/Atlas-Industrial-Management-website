from django.contrib import admin
from django.db.models import Count

from core.admin_mixins import (
    AtlasTranslationAdmin,
    ImagePreviewMixin,
    OrderedContentAdmin,
    render_image_preview_large,
)
from .models import (
    Advantage,
    Capability,
    Certification,
    CompanyInfo,
    FAQ,
    Industry,
    Milestone,
    ProcessStep,
    Service,
    Statistic,
    Technology,
    Testimonial,
)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(ImagePreviewMixin, AtlasTranslationAdmin):
    preview_field = 'logo'
    list_display = ('name', 'phone', 'email')
    readonly_fields = ('logo_preview', 'hero_image_preview', 'about_image_preview')

    fieldsets = (
        ('هویت شرکت', {
            'fields': ('name', 'logo', 'logo_preview', 'tagline'),
            'description': 'لوگو اختیاری است؛ در نبود آن نشان برداری اطلس استفاده می‌شود.',
        }),
        ('صفحه اصلی — بخش نخست', {
            'fields': ('hero_title', 'hero_text', 'hero_image', 'hero_image_preview'),
            'description': 'تیتر، متن و تصویر بالای صفحه اصلی. اینجا درباره‌ی شرکت بنویسید، نه یک محصول خاص.',
        }),
        ('صفحه اصلی — معرفی شرکت', {
            'fields': ('intro_title', 'intro_text'),
        }),
        ('صفحه درباره ما', {
            'fields': ('about_text', 'about_image', 'about_image_preview', 'mission_text', 'vision_text'),
        }),
        ('بازار جهانی و صادرات', {
            'fields': ('global_title', 'global_text'),
            'description': 'موقعیت شرکت برای ورود به بازارهای بین‌المللی. فقط آنچه قابل اثبات است بنویسید.',
        }),
        ('بخش فراخوان (CTA)', {
            'fields': ('cta_title', 'cta_text'),
        }),
        ('اطلاعات تماس', {
            'fields': (
                'address', 'postal_code', 'phone', 'secondary_phone', 'fax',
                'email', 'sales_email', 'working_hours', 'map_embed_url',
            ),
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('linkedin_url', 'instagram_url', 'telegram_url', 'whatsapp_url', 'youtube_url'),
            'classes': ('collapse',),
        }),
        ('سئو و اشتراک‌گذاری', {
            'fields': ('meta_description', 'og_image'),
            'classes': ('collapse',),
        }),
        ('تنظیمات فرم تماس', {
            'fields': ('notification_email',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='پیش‌نمایش لوگو')
    def logo_preview(self, obj):
        return render_image_preview_large(obj.logo)

    @admin.display(description='پیش‌نمایش تصویر صفحه اول')
    def hero_image_preview(self, obj):
        return render_image_preview_large(obj.hero_image)

    @admin.display(description='پیش‌نمایش تصویر درباره ما')
    def about_image_preview(self, obj):
        return render_image_preview_large(obj.about_image)

    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # حذف این رکورد باعث خطای صفحه اصلی می‌شود، پس مسدود است.
        return False


class PageContentAdmin(ImagePreviewMixin, AtlasTranslationAdmin):
    """
    پایه‌ی پنل برای مدل‌هایی که صفحه‌ی اختصاصی دارند (فناوری، صنعت).
    """
    list_display = ('title', 'icon', 'page_state', 'product_count', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description', 'body')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('order', 'id')
    readonly_fields = ('image_preview_large',)

    fieldsets = (
        ('معرفی', {
            'fields': ('title', 'slug', 'icon', 'description'),
            'description': 'توضیح کوتاه در کارت‌های صفحه اصلی و فهرست‌ها دیده می‌شود.',
        }),
        ('صفحه اختصاصی', {
            'fields': ('body',),
            'description': 'اگر این فیلد را پر کنید، صفحه‌ی اختصاصی این مورد ساخته و '
                           'از فهرست‌ها به آن لینک داده می‌شود. خالی بگذارید تا فقط کارت بماند.',
        }),
        ('تصویر', {'fields': ('image', 'image_preview_large'), 'classes': ('collapse',)}),
        ('سئو', {'fields': ('meta_description',), 'classes': ('collapse',)}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_products=Count('products', distinct=True))

    @admin.display(description='صفحه اختصاصی', boolean=True)
    def page_state(self, obj):
        return obj.has_page

    @admin.display(description='محصولات مرتبط', ordering='_products')
    def product_count(self, obj):
        return getattr(obj, '_products', 0)


@admin.register(Technology)
class TechnologyAdmin(PageContentAdmin):
    pass


@admin.register(Industry)
class IndustryAdmin(PageContentAdmin):
    pass


@admin.register(Service)
class ServiceAdmin(ImagePreviewMixin, OrderedContentAdmin):
    list_display = ('title', 'icon', 'image_preview', 'order', 'is_active')
    fieldsets = (
        ('محتوا', {'fields': ('title', 'description', 'icon', 'image')}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )


@admin.register(Advantage)
class AdvantageAdmin(OrderedContentAdmin):
    pass


@admin.register(Capability)
class CapabilityAdmin(OrderedContentAdmin):
    pass


@admin.register(Certification)
class CertificationAdmin(ImagePreviewMixin, OrderedContentAdmin):
    list_display = ('title', 'issuer', 'image_preview', 'order', 'is_active')
    search_fields = ('title', 'description', 'issuer')
    fieldsets = (
        ('محتوا', {'fields': ('title', 'issuer', 'description', 'icon', 'image')}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )
@admin.register(Statistic)
class StatisticAdmin(AtlasTranslationAdmin):
    list_display = ('label', 'value', 'suffix', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('label',)
    ordering = ('order', 'id')

    fieldsets = (
        ('عدد', {'fields': ('value', 'suffix'), 'description': 'فقط اعداد واقعی و قابل اثبات شرکت.'}),
        ('عنوان', {'fields': ('label',)}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )


@admin.register(Milestone)
class MilestoneAdmin(AtlasTranslationAdmin):
    list_display = ('year', 'title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('year', 'title', 'description')
    ordering = ('order', 'id')

    fieldsets = (
        ('محتوا', {'fields': ('year', 'title', 'description')}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )


@admin.register(FAQ)
class FAQAdmin(AtlasTranslationAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')
    ordering = ('order', 'id')

    fieldsets = (
        ('محتوا', {'fields': ('question', 'answer')}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )


@admin.register(Testimonial)
class TestimonialAdmin(AtlasTranslationAdmin):
    list_display = ('author', 'role', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('author', 'role', 'quote')
    ordering = ('order', 'id')

    fieldsets = (
        ('نظر', {'fields': ('quote',)}),
        ('گوینده', {'fields': ('author', 'role')}),
        ('نمایش', {'fields': ('order', 'is_active')}),
    )


@admin.register(ProcessStep)
class ProcessStepAdmin(AtlasTranslationAdmin):
    list_display = ('step_number', 'title', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    ordering = ('step_number', 'id')

    fieldsets = (
        ('محتوا', {'fields': ('step_number', 'title', 'description')}),
        ('نمایش', {'fields': ('is_active',)}),
    )


admin.site.site_header = 'پنل مدیریت اطلس'
admin.site.site_title = 'مدیریت سایت اطلس'
admin.site.index_title = 'مدیریت محتوای وب‌سایت'

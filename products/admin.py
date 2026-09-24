from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from core.admin_mixins import (
    AtlasTranslationAdmin,
    ImagePreviewMixin,
    TranslationTabularInline,
    render_image_preview,
)
from .models import (
    Category,
    Product,
    ProductApplication,
    ProductDocument,
    ProductFeature,
    ProductImage,
    ProductSpecification,
)


class ProductImageInline(TranslationTabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'preview', 'caption', 'order')
    readonly_fields = ('preview',)
    ordering = ('order', 'id')
    verbose_name = 'تصویر گالری'
    verbose_name_plural = 'گالری تصاویر'

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        return render_image_preview(getattr(obj, 'image', None), height=64)


class ProductSpecificationInline(TranslationTabularInline):
    model = ProductSpecification
    extra = 3
    fields = ('group', 'label', 'value', 'unit', 'is_highlight', 'order')
    ordering = ('order', 'id')
    verbose_name = 'مشخصه فنی'
    verbose_name_plural = 'جدول مشخصات فنی'


class ProductFeatureInline(TranslationTabularInline):
    model = ProductFeature
    extra = 2
    fields = ('title', 'description', 'order')
    ordering = ('order', 'id')
    verbose_name = 'ویژگی'
    verbose_name_plural = 'ویژگی‌های کلیدی'


class ProductApplicationInline(TranslationTabularInline):
    model = ProductApplication
    extra = 2
    fields = ('title', 'description', 'order')
    ordering = ('order', 'id')
    verbose_name = 'کاربرد'
    verbose_name_plural = 'کاربردها'


class ProductDocumentInline(TranslationTabularInline):
    model = ProductDocument
    extra = 1
    fields = ('title', 'file', 'order')
    ordering = ('order', 'id')
    verbose_name = 'مدرک فنی'
    verbose_name_plural = 'مدارک و کاتالوگ‌ها'


@admin.register(Category)
class CategoryAdmin(AtlasTranslationAdmin):
    list_display = ('name', 'slug', 'icon', 'product_count', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('order', 'name')

    fieldsets = (
        ('خط محصول', {'fields': ('name', 'slug', 'icon', 'description')}),
        ('نمایش', {'fields': ('order',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_product_count=Count('products'))

    @admin.display(description='تعداد محصول', ordering='_product_count')
    def product_count(self, obj):
        return getattr(obj, '_product_count', obj.products.count())


@admin.register(Product)
class ProductAdmin(ImagePreviewMixin, AtlasTranslationAdmin):
    list_display = (
        'image_preview', 'name', 'model_code', 'category',
        'is_featured', 'is_active', 'order', 'updated_at',
    )
    list_display_links = ('image_preview', 'name')
    list_filter = ('is_active', 'is_featured', 'category', 'technologies', 'industries')
    search_fields = ('name', 'model_code', 'tagline', 'short_description', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'is_active', 'order')
    list_select_related = ('category',)
    filter_horizontal = ('technologies', 'industries')
    readonly_fields = ('created_at', 'updated_at', 'main_image_preview', 'gallery_summary')
    date_hierarchy = 'created_at'
    save_on_top = True
    list_per_page = 25

    inlines = [
        ProductSpecificationInline,
        ProductFeatureInline,
        ProductApplicationInline,
        ProductImageInline,
        ProductDocumentInline,
    ]

    fieldsets = (
        ('شناسه محصول', {
            'fields': ('name', 'slug', 'model_code', 'tagline'),
        }),
        ('جایگاه در ساختار شرکت', {
            'fields': ('category', 'technologies', 'industries'),
            'description': 'خط محصول، حوزه‌های فناوری و صنعت‌ها. همین ارتباط‌ها '
                           'باعث می‌شوند محصول به‌صورت خودکار در صفحات مربوطه دیده شود.',
        }),
        ('تصویر', {
            'fields': ('image', 'main_image_preview', 'gallery_summary'),
        }),
        ('متن‌ها', {
            'fields': ('short_description', 'description', 'specifications'),
        }),
        ('سئو', {
            'fields': ('meta_description',),
            'classes': ('collapse',),
        }),
        ('نمایش و وضعیت', {
            'fields': ('is_active', 'is_featured', 'order', 'created_at', 'updated_at'),
        }),
    )

    @admin.display(description='پیش‌نمایش تصویر اصلی')
    def main_image_preview(self, obj):
        return render_image_preview(getattr(obj, 'image', None), height=200, max_width=340)

    @admin.display(description='تعداد تصاویر گالری')
    def gallery_summary(self, obj):
        if not obj.pk:
            return 'پس از ذخیره‌ی محصول می‌توانید تصاویر گالری را اضافه کنید.'
        return format_html('<strong>{}</strong> تصویر', obj.images.count())

    @admin.action(description='فعال کردن نمایش در سایت')
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} محصول فعال شد.')

    @admin.action(description='غیرفعال کردن نمایش در سایت')
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} محصول غیرفعال شد.')

    @admin.action(description='افزودن به محصولات شاخص')
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} محصول به محصولات شاخص اضافه شد.')

    actions = ['make_active', 'make_inactive', 'make_featured']

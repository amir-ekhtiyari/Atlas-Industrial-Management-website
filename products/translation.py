from modeltranslation.translator import register, TranslationOptions

from .models import (
    Category,
    Product,
    ProductApplication,
    ProductDocument,
    ProductFeature,
    ProductImage,
    ProductSpecification,
)


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'tagline', 'short_description', 'description', 'specifications', 'meta_description')


@register(ProductImage)
class ProductImageTranslationOptions(TranslationOptions):
    fields = ('caption',)


@register(ProductSpecification)
class ProductSpecificationTranslationOptions(TranslationOptions):
    fields = ('group', 'label', 'value', 'unit')


@register(ProductFeature)
class ProductFeatureTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(ProductApplication)
class ProductApplicationTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(ProductDocument)
class ProductDocumentTranslationOptions(TranslationOptions):
    fields = ('title',)

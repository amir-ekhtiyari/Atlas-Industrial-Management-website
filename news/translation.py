from modeltranslation.translator import register, TranslationOptions
from .models import Post, PostCategory


@register(PostCategory)
class PostCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'summary', 'body', 'meta_description')

from modeltranslation.translator import register, TranslationOptions

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


@register(CompanyInfo)
class CompanyInfoTranslationOptions(TranslationOptions):
    fields = (
        'name', 'tagline', 'hero_text', 'about_text',
        'hero_title', 'intro_title', 'intro_text',
        'mission_text', 'vision_text',
        'global_title', 'global_text',
        'cta_title', 'cta_text',
        'address', 'working_hours', 'meta_description',
    )


@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Advantage)
class AdvantageTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Technology)
class TechnologyTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'body', 'meta_description')


@register(Industry)
class IndustryTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'body', 'meta_description')


@register(Capability)
class CapabilityTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(Certification)
class CertificationTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'issuer')


@register(Statistic)
class StatisticTranslationOptions(TranslationOptions):
    fields = ('label', 'suffix')


@register(Milestone)
class MilestoneTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')


@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ('quote', 'author', 'role')


@register(ProcessStep)
class ProcessStepTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

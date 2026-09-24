from django import forms
from django.utils.translation import gettext_lazy as _

from products.models import Product
from .models import ContactMessage

# کلاس ظاهری فیلدها در style.css با نام `.field` تعریف شده است.
TEXT_INPUT_CLASS = 'field'


class ContactForm(forms.ModelForm):
    """
    فرم تماس. فیلد `website` یک تله‌ی ساده برای ربات‌ها (honeypot) است؛
    برای کاربر واقعی پنهان می‌ماند و اگر پر شود، فرم رد می‌شود.
    """

    website = forms.CharField(
        required=False,
        label='',
        widget=forms.TextInput(attrs={
            'tabindex': '-1',
            'autocomplete': 'off',
            'aria-hidden': 'true',
            'class': 'hp-field',
        }),
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'company', 'topic', 'subject', 'message', 'related_product']

        labels = {
            'name': _('نام و نام خانوادگی'),
            'email': _('ایمیل'),
            'phone': _('شماره تماس'),
            'company': _('نام سازمان'),
            'topic': _('موضوع درخواست'),
            'subject': _('موضوع'),
            'message': _('متن پیام'),
            'related_product': _('محصول مرتبط'),
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': TEXT_INPUT_CLASS,
                'placeholder': _('نام و نام خانوادگی خود را وارد کنید'),
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': TEXT_INPUT_CLASS,
                'placeholder': 'example@email.com',
                'autocomplete': 'email',
                'dir': 'ltr',
            }),
            'phone': forms.TextInput(attrs={
                'class': TEXT_INPUT_CLASS,
                'placeholder': _('اختیاری'),
                'autocomplete': 'tel',
                'dir': 'ltr',
            }),
            'company': forms.TextInput(attrs={
                'class': TEXT_INPUT_CLASS,
                'placeholder': _('اختیاری'),
                'autocomplete': 'organization',
            }),
            'topic': forms.Select(attrs={'class': TEXT_INPUT_CLASS}),
            'subject': forms.TextInput(attrs={
                'class': TEXT_INPUT_CLASS,
                'placeholder': _('موضوع پیام شما'),
            }),
            'message': forms.Textarea(attrs={
                'class': TEXT_INPUT_CLASS,
                'placeholder': _('پیام خود را بنویسید...'),
                'rows': 6,
            }),
            'related_product': forms.Select(attrs={'class': TEXT_INPUT_CLASS}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['related_product'].queryset = Product.objects.active().order_by('order', 'name')
        self.fields['related_product'].required = False
        self.fields['related_product'].empty_label = _('— انتخاب کنید (اختیاری) —')
        self.fields['company'].required = False

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError(_('ارسال فرم ناموفق بود.'))
        return ''

    def clean_message(self):
        message = (self.cleaned_data.get('message') or '').strip()
        if len(message) < 10:
            raise forms.ValidationError(_('متن پیام باید حداقل ۱۰ کاراکتر باشد.'))
        return message

    def clean_name(self):
        return (self.cleaned_data.get('name') or '').strip()

    def clean_subject(self):
        return (self.cleaned_data.get('subject') or '').strip()

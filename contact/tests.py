from django.core import mail
from django.test import TestCase
from django.urls import reverse

from core.models import FAQ
from core.tests import make_company
from products.tests import make_product

from .forms import ContactForm
from .models import ContactMessage

VALID_DATA = {
    'name': 'کاربر آزمایشی',
    'email': 'user@example.com',
    'phone': '09120000000',
    'company': 'شرکت نمونه',
    'topic': ContactMessage.Topic.SALES,
    'subject': 'استعلام قیمت',
    'message': 'لطفاً مشخصات فنی و قیمت دستگاه را ارسال کنید.',
    'website': '',
}


class ContactFormTests(TestCase):
    def test_valid_data_is_accepted(self):
        self.assertTrue(ContactForm(data=VALID_DATA).is_valid())

    def test_honeypot_rejects_bots(self):
        form = ContactForm(data={**VALID_DATA, 'website': 'http://spam.example'})
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_short_message_is_rejected(self):
        form = ContactForm(data={**VALID_DATA, 'message': 'کوتاه'})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_name_and_subject_are_trimmed(self):
        form = ContactForm(data={**VALID_DATA, 'name': '  علی  ', 'subject': '  سلام  '})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'علی')
        self.assertEqual(form.cleaned_data['subject'], 'سلام')

    def test_related_product_choices_exclude_inactive(self):
        make_product(slug='active-unit')
        make_product(slug='hidden-unit', is_active=False)
        slugs = [p.slug for p in ContactForm().fields['related_product'].queryset]
        self.assertEqual(slugs, ['active-unit'])

    def test_optional_fields_are_not_required(self):
        form = ContactForm(data={**VALID_DATA, 'phone': '', 'company': ''})
        self.assertTrue(form.is_valid())


class ContactViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = make_company(notification_email='sales@example.com')
        cls.product = make_product(slug='og-500', name='اکسیژن‌ساز ۵۰۰')
        FAQ.objects.create(question='چطور سفارش دهیم؟', answer='از همین فرم', order=10)

    def test_get_renders_form_and_faqs(self):
        response = self.client.get(reverse('contact:form'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ContactForm)
        self.assertTrue(response.context['faqs'])

    def test_post_saves_message_and_redirects(self):
        response = self.client.post(reverse('contact:form'), VALID_DATA)
        self.assertRedirects(response, reverse('contact:form'))
        message = ContactMessage.objects.get()
        self.assertEqual(message.name, 'کاربر آزمایشی')
        self.assertEqual(message.status, ContactMessage.Status.NEW)
        self.assertFalse(message.is_read)

    def test_post_sends_notification_when_email_configured(self):
        self.client.post(reverse('contact:form'), VALID_DATA)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('استعلام قیمت', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['sales@example.com'])

    def test_no_notification_without_configured_email(self):
        self.company.notification_email = ''
        super(type(self.company), self.company).save()
        self.client.post(reverse('contact:form'), VALID_DATA)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_invalid_post_does_not_create_message(self):
        response = self.client.post(reverse('contact:form'), {**VALID_DATA, 'email': 'not-an-email'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertTrue(response.context['form'].errors)

    def test_product_query_param_prefills_form(self):
        response = self.client.get(reverse('contact:form'), {'product': self.product.slug})
        initial = response.context['form'].initial
        self.assertEqual(initial['related_product'], self.product.pk)
        self.assertIn(self.product.name, initial['subject'])

    def test_unknown_product_param_is_ignored(self):
        response = self.client.get(reverse('contact:form'), {'product': 'no-such-product'})
        self.assertNotIn('related_product', response.context['form'].initial)

    def test_topic_query_param_prefills_topic(self):
        response = self.client.get(reverse('contact:form'), {'topic': 'technical'})
        self.assertEqual(response.context['form'].initial['topic'], 'technical')

    def test_invalid_topic_param_is_ignored(self):
        response = self.client.get(reverse('contact:form'), {'topic': 'nonsense'})
        self.assertNotIn('topic', response.context['form'].initial)

    def test_honeypot_submission_is_not_saved(self):
        self.client.post(reverse('contact:form'), {**VALID_DATA, 'website': 'spam'})
        self.assertEqual(ContactMessage.objects.count(), 0)

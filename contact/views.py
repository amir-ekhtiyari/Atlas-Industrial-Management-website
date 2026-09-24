import logging

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from core.models import FAQ
from core.utils import get_company
from products.models import Product
from .forms import ContactForm

logger = logging.getLogger(__name__)


def _notify_admin(company, instance):
    """
    ارسال ایمیل اطلاع‌رسانی به شرکت. اگر ایمیل مقصد تنظیم نشده باشد یا ارسال
    شکست بخورد، پیام کاربر همچنان در پنل ذخیره شده است و خطایی به او نشان
    داده نمی‌شود.
    """
    recipient = getattr(company, 'notification_email', '') or ''
    if not recipient:
        return

    lines = [
        f"نام: {instance.name}",
        f"ایمیل: {instance.email}",
        f"تلفن: {instance.phone or '-'}",
        f"سازمان: {instance.company or '-'}",
        f"موضوع درخواست: {instance.get_topic_display()}",
        f"محصول مرتبط: {instance.related_product.name if instance.related_product else '-'}",
        '',
        instance.message,
    ]
    try:
        send_mail(
            subject=f"[فرم تماس سایت] {instance.subject}",
            message='\n'.join(lines),
            from_email=None,
            recipient_list=[recipient],
            fail_silently=True,
        )
    except Exception:
        logger.exception('ارسال ایمیل اطلاع‌رسانی فرم تماس ناموفق بود.')


def contact_view(request):
    company = get_company(request)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            instance = form.save()
            _notify_admin(company, instance)
            messages.success(
                request,
                _('پیام شما با موفقیت ارسال شد. به‌زودی با شما تماس خواهیم گرفت.'),
            )
            return redirect('contact:form')
        messages.error(request, _('لطفاً خطاهای فرم را بررسی کنید.'))
    else:
        initial = {}
        product_slug = request.GET.get('product')
        if product_slug:
            product = Product.objects.active().filter(slug=product_slug).first()
            if product:
                initial['related_product'] = product.pk
                initial['subject'] = _('استعلام درباره %(product)s') % {'product': product.name}
        topic = request.GET.get('topic')
        if topic in dict(ContactForm.Meta.model.Topic.choices):
            initial['topic'] = topic
        form = ContactForm(initial=initial)

    context = {
        'form': form,
        'company': company,
        'faqs': FAQ.objects.active(),
    }
    return render(request, 'contact/contact.html', context)

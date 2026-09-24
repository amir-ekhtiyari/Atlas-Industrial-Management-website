from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import SITEMAPS
from core.views import qr_code, robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('qr-code.png', qr_code, name='qr_code'),
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('products/', include('products.urls')),
    path('insights/', include('news.urls')),
    path('team/', include('team.urls')),
    path('contact/', include('contact.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

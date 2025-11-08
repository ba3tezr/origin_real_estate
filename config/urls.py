"""
URL configuration for Origin App Real Estate Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Add i18n patterns for language switching
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('owners/', include('apps.owners.urls')),
    path('clients/', include('apps.clients.urls')),
    path('properties/', include('apps.properties.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('maintenance/', include('apps.maintenance.urls')),
    path('financial/', include('apps.financial.urls')),
    # path('reports/', include('apps.reports.urls')),  # TODO: قيد التطوير
    path('api/v1/', include('api.urls')),  # REST API
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Origin App Administration"
admin.site.site_title = "Origin App"
admin.site.index_title = "Real Estate Management System"

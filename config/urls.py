from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("org/", include("apps.orgs.urls")),
    path("pilot/", include("apps.pilots.urls")),
    path("billing/", include("apps.billing.urls")),
    path("onboarding/", include("apps.onboarding.urls")),
    path("documents/", include("apps.documents.urls")),
    path("chat/", include("apps.chat.urls")),
    path("", include("apps.web.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


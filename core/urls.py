from django.contrib import admin
from django.urls import path, include
from accounts.views_profile import update_profile

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # TEST: Direct URL mapping to bypass any routing conflicts
    path("direct-profile-update/", update_profile, name="direct_profile_update"),

    path("auth/", include("accounts.urls")),
    path("accounts/", include("accounts.urls")),
    
    # Move pitches to api/ prefix to avoid conflicts
    path("api/", include("pitches.urls")),
    path("api/", include("investor_posts.urls")),

]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
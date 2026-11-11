from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from portfolio.views import not_found
urlpatterns = [path('admin/', admin.site.urls),path('', include('portfolio.urls'))]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = not_found

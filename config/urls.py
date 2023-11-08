from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from common import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', include('chat.urls')),
    path('rps/', include('rps.urls')),
    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
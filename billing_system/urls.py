from django.contrib import admin
from django.urls import path, include
from billing import urls
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(urls)),
    path('api/schema/', SpectacularSwaggerView.as_view(), name='schema'),
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='schema-docs'),
]

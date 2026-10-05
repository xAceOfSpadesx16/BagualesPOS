from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/', include('products.urls')),
    path('api/', include('clients.urls')),
    path('api/', include('inventory.urls')),
    path('api/', include('sales.urls')),
    path('api/', include('users.urls')),
    path('api/', include('records.urls')),
    path('api/', include('cash.urls')),
    path('api/', include('devices.urls')),
]

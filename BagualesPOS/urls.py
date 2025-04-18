from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView, LoginView
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='sales', permanent=True)),
    path('admin/', admin.site.urls),
    path('ventas/', include('sales.urls')),
    path('registros/', include('records.urls')),
    path('inventario/', include('inventory.urls')),
    path('clientes/', include('clients.urls')),
    # path('productos/', include('products.urls')),
    path('administracion/', include('administration.urls')),
    path('users/', include('users.urls')),
    path(
        'login/',
        LoginView.as_view(
            template_name='login.html',
        ),
        name='login'
    ),
    path('logout/', LogoutView.as_view(), name='logout'),
]

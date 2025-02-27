from django.contrib import admin

from sales.models import PayMethod, Sale, SaleDetail


admin.site.register([PayMethod, Sale, SaleDetail])
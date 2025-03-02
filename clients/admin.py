from django.contrib import admin
from clients.models import Client, CustomerBalanceRecord


admin.site.register([Client, CustomerBalanceRecord])


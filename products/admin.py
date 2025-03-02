from django.contrib import admin

from products.models import Product, Color, Materials, LetterSize, Supplier, Gender


admin.site.register([Product, Color, Materials, LetterSize, Supplier, Gender])
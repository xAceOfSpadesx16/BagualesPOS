from django.contrib import admin

from products.models import Product, Color, Materials, LetterSize, Supplier, Gender, Brand, Category, Season, Subcategory


admin.site.register([Product, Color, Materials, LetterSize, Supplier, Gender, Brand, Category, Season, Subcategory])
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    BrandViewSet,
    CategoryViewSet,
    SubcategoryViewSet,
    ColorViewSet,
    GenderViewSet,
    LetterSizeViewSet,
    MaterialsViewSet,
    SeasonViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'genders', GenderViewSet)
router.register(r'letter-sizes', LetterSizeViewSet)
router.register(r'materials', MaterialsViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'suppliers', SupplierViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from django.views.generic import RedirectView
from products.views import BrandCreateView, BrandUpdateView, BrandListView, BrandDeleteView
from products.views import CategoryCreateView, CategoryUpdateView, CategoryListView, CategoryDeleteView
from products.views import ColorCreateView, ColorUpdateView, ColorListView, ColorDeleteView
from products.views import GenderCreateView, GenderUpdateView, GenderListView, GenderDeleteView
from products.views import LetterSizeCreateView, LetterSizeUpdateView, LetterSizeListView, LetterSizeDeleteView
from products.views import MaterialsCreateView, MaterialsUpdateView, MaterialsListView, MaterialsDeleteView
from products.views import SeasonCreateView, SeasonUpdateView, SeasonListView, SeasonDeleteView
from products.views import SupplierCreateView, SupplierUpdateView, SupplierListView, SupplierDeleteView


urlpatterns = [
    path('', RedirectView.as_view(pattern_name='product_list', permanent=True), name='administration'),
    path('productos/', include('products.urls')),
]

brand_patterns = [
    path('marcas/', BrandListView.as_view(), name='brand_administration'),
    path('marcas/create/', BrandCreateView.as_view(), name='brand_create'),
    path('marcas/update/<int:pk>/', BrandUpdateView.as_view(), name='brand_update'),
    path('marcas/delete/<int:pk>/', BrandDeleteView.as_view(), name='brand_delete'),
]


urlpatterns += brand_patterns

category_patterns = [
    path('categorias/', CategoryListView.as_view(), name='category_administration'),
    path('categorias/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categorias/update/<int:pk>/', CategoryUpdateView.as_view(), name='category_update'),
    path('categorias/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_delete'),
]

urlpatterns += category_patterns    

color_patterns = [
    path('colores/', ColorListView.as_view(), name='color_administration'),
    path('colores/create/', ColorCreateView.as_view(), name='color_create'),
    path('colores/update/<int:pk>/', ColorUpdateView.as_view(), name='color_update'),
    path('colores/delete/<int:pk>/', ColorDeleteView.as_view(), name='color_delete'),
]

urlpatterns += color_patterns

gender_patterns = [
    path('generos/', GenderListView.as_view(), name='gender_administration'),
    path('generos/create/', GenderCreateView.as_view(), name='gender_create'),
    path('generos/update/<int:pk>/', GenderUpdateView.as_view(), name='gender_update'),
    path('generos/delete/<int:pk>/', GenderDeleteView.as_view(), name='gender_delete'),
]

urlpatterns += gender_patterns


letter_size_patterns = [
    path('talles/', LetterSizeListView.as_view(), name='letter_size_administration'),
    path('talles/create/', LetterSizeCreateView.as_view(), name='letter_size_create'),
    path('talles/update/<int:pk>/', LetterSizeUpdateView.as_view(), name='letter_size_update'),
    path('talles/delete/<int:pk>/', LetterSizeDeleteView.as_view(), name='letter_size_delete'),
]

urlpatterns += letter_size_patterns

materials_patterns = [
    path('materiales/', MaterialsListView.as_view(), name='materials_administration'),
    path('materiales/create/', MaterialsCreateView.as_view(), name='materials_create'),
    path('materiales/update/<int:pk>/', MaterialsUpdateView.as_view(), name='materials_update'),
    path('materiales/delete/<int:pk>/', MaterialsDeleteView.as_view(), name='materials_delete'),
    ]

urlpatterns += materials_patterns

season_patterns = [
    path('temporadas/', SeasonListView.as_view(), name='season_administration'),
    path('temporadas/create/', SeasonCreateView.as_view(), name='season_create'),
    path('temporadas/update/<int:pk>/', SeasonUpdateView.as_view(), name='season_update'),
    path('temporadas/delete/<int:pk>/', SeasonDeleteView.as_view(), name='season_delete'),
]

urlpatterns += season_patterns

supplier_patterns = [
    path('proveedores/', SupplierListView.as_view(), name='supplier_administration'),
    path('proveedores/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('proveedores/update/<int:pk>/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('proveedores/delete/<int:pk>/', SupplierDeleteView.as_view(), name='supplier_delete'),
]

urlpatterns += supplier_patterns


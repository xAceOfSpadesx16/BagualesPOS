from django.views.generic import TemplateView, DeleteView, CreateView, UpdateView
from sales.models import Sale, SaleDetail
from dal import autocomplete
from django.db.models import Q

from sales.forms import SearchProductForm
from products.models import Product

class SalesIndex(TemplateView):
    template_name = 'sales.html'

    def get_context_data(self, **kwargs):
        sale = Sale.objects.get_table_active_sale(self.request.user)
        if not sale:
            sale: Sale = Sale.objects.create(seller=self.request.user)
        kwargs['sale'] = sale
        kwargs['form'] = SearchProductForm()
        return super().get_context_data(**kwargs)

class SaleDetailDelete(DeleteView):
    model = SaleDetail

class SaleDetailCreate(CreateView):
    model = SaleDetail
    fields = ['product', 'quantity']

class SaleDetailUpdate(UpdateView):
    model = SaleDetail
    fields = ['product', 'quantity']




class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.select_related('letter_size', 'gender', 'material', 'color', 'brand', 'category', 'season').all()
        search_term = self.request.GET.get('q', '')
        if search_term:
            search_terms = search_term.split()
            q_objects = []
            for term in search_terms:
                q_objects.append(
                    Q(name__istartwith=term) |
                    Q(numeric_size__istartwith=term) |
                    Q(details__istartwith=term) |
                    Q(letter_size__name__istartwith=term) |
                    Q(gender__name__istartwith=term) |
                    Q(material__name__istartwith=term) |
                    Q(color__name__istartwith=term) |
                    Q(brand__name__istartwith=term) |
                    Q(category__name__istartwith=term) |
                    Q(season__name__istartwith=term) |
                    Q(internal_code__istartwith=term)
                )
            qs = qs.filter(*q_objects)
        return qs

    def get_result_label(self, item: Product):
        return f"{item.name} {item.color.name} {item.brand.name} T-{item.letter_size.name if item.letter_size else item.numeric_size}"

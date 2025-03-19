from django.views.generic import TemplateView, CreateView, View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpRequest
from dal import autocomplete

from json import loads

from sales.models import Sale, SaleDetail

from sales.forms import SearchProductForm
from products.models import Product

class SalesIndex(TemplateView):
    template_name = 'sales.html'

    def get_context_data(self, **kwargs):
        sale = Sale.objects.get_table_active_sale(self.request.user)
        if not sale:
            sale: Sale = Sale.objects.create(seller=self.request.user)
            self.request.session['active_sale_id'] = sale.id
        kwargs['sale'] = sale
        kwargs['form'] = SearchProductForm()
        return super().get_context_data(**kwargs)

class SaleDetailDelete(View):
    http_method_names = ['delete']

    def delete(self, request: HttpRequest, pk, *args, **kwargs):
        
        sale_detail = get_object_or_404(SaleDetail, id=pk)
        sale_detail.delete()
        
        return JsonResponse({"message": "Registro eliminado con éxito", "total_sale_amount": sale_detail.order.formatted_total_amount}, status=200)
        
class SaleDetailCreate(CreateView):
    model = SaleDetail

    http_method_names = ['post']


    def post(self, request: HttpRequest, *args, **kwargs):
        form = SearchProductForm(loads(request.body), request=self.request)
        if form.is_valid():
            instance: SaleDetail = form.save()
            product = instance.product
            quantity = instance.quantity
            sale_price = instance.formatted_sale_price
            total_price = instance.formatted_total_price


            return JsonResponse({
                'product': {
                    'name': product.name,
                },
                'quantity': quantity,
                'sale_price': sale_price,
                'total_price': total_price,
                'total_sale_amount': instance.order.formatted_total_amount,
                'id': instance.pk,
            })
        else:
            print(form.errors)
            return JsonResponse({'error': form.errors}, status=400)



class SaleQuantityDetailUpdate(View):

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'patch':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def patch(self, request: HttpRequest, pk, *args, **kwargs):
        body = loads(request.body)
        quantity = body.get('quantity')
        sale_detail = get_object_or_404(SaleDetail, id=pk)
        sale_detail.quantity = int(quantity)
        sale_detail.save()
        data = {
            'quantity': sale_detail.quantity,
            'sale_price': sale_detail.formatted_sale_price,
            'total_price': sale_detail.formatted_total_price,
            'total_sale_amount': sale_detail.order.formatted_total_amount,
        }
        return JsonResponse(data)


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.select_related('letter_size', 'gender', 'material', 'color', 'brand', 'category', 'season').all().order_by('name')
        search_term = self.request.GET.get('q', '')
        if search_term:
            search_terms = search_term.split()
            q_objects = []
            for term in search_terms:
                q_objects.append(
                    Q(name__istartswith=term) |
                    Q(numeric_size__istartswith=term) |
                    Q(details__istartswith=term) |
                    Q(letter_size__name__istartswith=term) |
                    Q(gender__name__istartswith=term) |
                    Q(material__name__istartswith=term) |
                    Q(color__name__istartswith=term) |
                    Q(brand__name__istartswith=term) |
                    Q(category__name__istartswith=term) |
                    Q(season__name__istartswith=term) |
                    Q(internal_code__istartswith=term)
                )
            qs = qs.filter(*q_objects)
        return qs

    def get_result_label(self, item: Product):
        return f"{item.name} {item.color.name} {item.brand.name} T-{item.letter_size.name if item.letter_size else item.numeric_size}"

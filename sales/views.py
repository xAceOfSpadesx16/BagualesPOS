from django.views.generic import TemplateView, DeleteView
from sales.models import Sale

# Create your views here.

class SalesIndex(TemplateView):
    template_name = 'sales.html'

    def get_context_data(self, **kwargs):
        sale = Sale.objects.get_table_active_sale(self.request.user)
        if not sale:
            sale: Sale = Sale.objects.create(seller=self.request.user)
        kwargs['sale'] = sale
        return super().get_context_data(**kwargs)

class SaleDetailDelete(DeleteView):
    model = Sale
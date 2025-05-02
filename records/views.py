from django.views.generic import View, TemplateView
from django.views.generic.list import ListView

from sales.models import Sale

class RecordsIndex(ListView):
    model = Sale
    context_object_name = 'sales'
    paginate_by = 8
    template_name = 'records.html'
    queryset = Sale.objects.select_related('client', 'pay_method').order_by('-id').all()

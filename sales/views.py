from django.views.generic import TemplateView

# Create your views here.

class SalesIndex(TemplateView):
    template_name = 'sales.html'

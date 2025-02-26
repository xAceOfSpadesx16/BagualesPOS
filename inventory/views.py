from django.views.generic import TemplateView


class InventoryIndex(TemplateView):
    template_name = 'inventory.html'
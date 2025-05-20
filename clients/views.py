from django.db.models import Q
from django.views.generic import ListView
from dal import autocomplete

from clients.models import Client

class ClientsListView(ListView):
    template_name = 'clients_list.html'
    model = Client
    context_object_name = 'clients'

class ClientCCListView(ListView):
    template_name = 'clients_cc_list.html'
    model = Client
    context_object_name = 'cc_clients'
    queryset = Client.objects.filter(approved_customer_account=True)


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Client.objects.all().order_by('name')
        search_term = self.request.GET.get('q', '')
        if search_term:
            search_terms = search_term.split()
            q_objects = []
            for term in search_terms:
                q_objects.append(
                    Q(name__istartswith=term) |
                    Q(last_name__istartswith=term) |
                    Q(dni__istartswith=term) |
                    Q(cuit__istartswith=term)
                )
            qs = qs.filter(*q_objects)
            
        return qs
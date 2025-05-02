from django.db.models import Q

from dal import autocomplete

from clients.models import Client

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
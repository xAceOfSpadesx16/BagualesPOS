import json
from functools import reduce
import operator
from django.db.models import Q
from django.views.generic import ListView
from dal import autocomplete
from django.views.generic.detail import DetailView
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.core.exceptions import ValidationError

from utils.mixins import FormValidationMixin, FetchRequestMixin
from django.views.generic.edit import CreateView, UpdateView

from clients.models import CustomerBalanceRecord, Client, CustomerAccount
from clients.choices import MovementType
from clients.forms import ClientForm, CustomerAccountForm

class ClientsListView(ListView):
    template_name = 'clients_list.html'
    model = Client
    context_object_name = 'clients'
    paginate_by = 20
    http_method_names = ['get']
    ordering = ['is_deleted', 'name', 'last_name']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('customer_account', 'customer_account__balance_records')


class ClientRetrieveView(DetailView):
    model = Client
    template_name = 'client_detail.html'
    context_object_name = 'client'
    http_method_names = ['get']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('customer_account')


class ClientCreateView(FormValidationMixin, FetchRequestMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'client_form.html'
    success_url = reverse_lazy('clients')
    http_method_names = ['get', 'post']



class ClientUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'client_form.html'
    success_url = reverse_lazy('clients')
    http_method_names = ['get', 'post']



class ClientDeleteView(FetchRequestMixin, View):
    http_method_names = ['post']
    success_url = reverse_lazy('clients')

    def post(self, request, pk, *args, **kwargs):
        client = get_object_or_404(Client, id=pk)
        client.soft_delete()
        return HttpResponseRedirect(self.success_url)


class ClientRestoreView(FetchRequestMixin, View):
    http_method_names = ['post']
    success_url = reverse_lazy('clients')

    def post(self, request, pk, *args, **kwargs):
        client = get_object_or_404(Client, id=pk)
        client.restore()
        return HttpResponseRedirect(self.success_url)


class ClientAutocomplete(autocomplete.Select2QuerySetView):
    http_method_names = ['get']

    def get_queryset(self):
        qs = Client.objects.filter(is_deleted=False).order_by('name')
        search_term = self.request.GET.get('q', '')
        if search_term and len(search_term) > 1:
            search_terms = search_term.split()
            q_objects = []
            for term in search_terms:
                q_objects.append(
                    Q(name__istartswith=term) |
                    Q(last_name__istartswith=term) |
                    Q(dni__istartswith=term) |
                    Q(cuit__istartswith=term)
                )
            qs = qs.filter(reduce(operator.or_, q_objects))
        return qs[:20]


class BalanceRecordDetailView(DetailView):
    model = CustomerBalanceRecord
    template_name = 'balance_record_detail.html'
    context_object_name = 'record'
    http_method_names = ['get']


class BalanceRecordCreateAPI(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            customer_account_id = data.get('customer_account_id')
            if not customer_account_id:
                return JsonResponse({'success': False, 'error': _('Current account ID is required.')}, status=400)
            amount = data.get('amount')
            movement_type = data.get('movement_type')
            notes = data.get('notes', '')
            reference = data.get('reference', '')
            related_to_id = data.get('related_to')
            sale_id = data.get('sale_id')
            created_by = request.user
            customer_account = get_object_or_404(CustomerAccount, pk=customer_account_id)
            related_to = None
            if related_to_id:
                related_to = get_object_or_404(CustomerBalanceRecord, pk=related_to_id)
            sale = None
            if sale_id:
                from sales.models import Sale
                sale = get_object_or_404(Sale, pk=sale_id)
            # Validación centralizada en el modelo
            try:
                with transaction.atomic():
                    record = CustomerBalanceRecord(
                        customer_account=customer_account,
                        amount=amount,
                        movement_type=movement_type,
                        notes=notes,
                        reference=reference,
                        related_to=related_to,
                        sale=sale,
                        created_by=created_by
                    )
                    record.full_clean()
                    record.save()
                return JsonResponse({'success': True, 'record': model_to_dict(record)}, status=201)
            except ValidationError as ve:
                return JsonResponse({'success': False, 'error': ve.message_dict}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class CustomerAccountSoftDelete(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        customer_account_id = kwargs.get('customer_account_id')
        customer_account = get_object_or_404(CustomerAccount, pk=customer_account_id)
        customer_account.deactivate()
        return JsonResponse({'success': True, 'message': _('Customer account deactivated successfully.')}, status=200)


class CustomerAccountDetailView(DetailView):
    model = CustomerAccount
    template_name = 'customer_account_detail.html'
    context_object_name = 'customer_account'
    http_method_names = ['get']

    def get_queryset(self):
        return super().get_queryset().select_related('client').prefetch_related('balance_records', 'balance_records__created_by', 'balance_records__related_to', 'balance_records__sale')


class CustomerAccountUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = CustomerAccount
    form_class = CustomerAccountForm
    template_name = 'customer_account_form.html'
    success_url = reverse_lazy('customer_account_detail')
    http_method_names = ['get', 'post']

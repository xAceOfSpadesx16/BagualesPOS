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
from clients.forms import ClientForm, CustomerAccountForm, BalanceRecordForm

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


class BalanceRecordCreateView(FormValidationMixin, CreateView):
    model = CustomerBalanceRecord
    form_class = BalanceRecordForm
    template_name = 'balance_record_form.html'
    http_method_names = ['get', 'post']
    object: CustomerBalanceRecord

    def get_success_url(self):
        return reverse_lazy('customer_account_detail', kwargs={'pk': self.object.customer_account.id})
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        account = get_object_or_404(CustomerAccount, pk=self.kwargs['pk'])
        kwargs.update(customer_account=account, created_by=self.request.user)
        return kwargs


class CustomerAccountSoftDelete(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        customer_account_id = kwargs.get('customer_account_id')
        customer_account = get_object_or_404(CustomerAccount, pk=customer_account_id)
        customer_account.deactivate()
        return JsonResponse({'success': True, 'message': _('Customer account deactivated successfully.')}, status=200)


class CustomerAccountDetailView(ListView):
    model = CustomerBalanceRecord
    template_name = 'customer_account_detail.html'
    context_object_name = 'balance_records'
    paginate_by = 20
    http_method_names = ['get']

    def get_queryset(self):
        return CustomerBalanceRecord.objects.filter(customer_account_id=self.kwargs['pk']).with_related().with_related_records()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_account'] = CustomerAccount.objects.select_related('client').get(pk=self.kwargs['pk'])
        return context


class CustomerAccountUpdateView(FormValidationMixin, FetchRequestMixin, UpdateView):
    model = CustomerAccount
    form_class = CustomerAccountForm
    template_name = 'customer_account_form.html'
    success_url = reverse_lazy('customer_account_detail')
    http_method_names = ['get', 'post']

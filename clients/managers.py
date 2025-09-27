from django.db.models import Sum
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models import (
    Sum, Manager, QuerySet, Q, F, Value, Exists, OuterRef, DecimalField, Case, When
)
from django.db.models.functions import Coalesce
from decimal import Decimal
from clients.choices import MovementType


class BalanceRecordsQueryset(QuerySet):

    #Filtered by MovementType
    def by_credit(self):
        return self.filter(movement_type=MovementType.CREDIT)
    
    def by_debit(self):
        return self.filter(movement_type=MovementType.DEBIT)

    def by_adjustment(self):
        return self.filter(movement_type=MovementType.ADJUSTMENT)

    def by_refund(self):
        return self.filter(movement_type=MovementType.REFUND)

    def by_reversal(self):
        return self.filter(movement_type=MovementType.REVERSAL)
    
    #Filtered by Reconciled
    def reconciled(self):
        return self.filter(reconciled=True)
    
    def unreconciled(self):
        return self.filter(reconciled=False)
    
    #Related
    def with_related(self):
        """
        Eagerly load, reducing the number of database queries (N+1).
        Only loads related fields that exist in CustomerBalanceRecord.
        """
        return self.select_related(
            'sale',
            'related_to',
            'created_by',
            'reconciled_by',
            'customer_account',
        )

    def with_related_records(self):
        """
        Eagerly load reverse relationships. Useful when accessing `related_records.all()` without extra queries.
        """
        return self.prefetch_related('related_records')

    #Filters
    def from_date(self, date):
        """
        Filters records from a given date (inclusive). Raises ValueError if date is not a date/datetime.
        """
        from datetime import date as dt_date, datetime
        if not isinstance(date, (dt_date, datetime)):
            raise ValueError("date must be a date or datetime object")
        return self.filter(created_at__gte=date)

    def to_date(self, date):
        """
        Filters records up to a given date (inclusive). Raises ValueError if date is not a date/datetime.
        """
        from datetime import date as dt_date, datetime
        if not isinstance(date, (dt_date, datetime)):
            raise ValueError("date must be a date or datetime object")
        return self.filter(created_at__lte=date)

    def search(self, query):
        """
        Performs a basic search on reference, client, or amount fields.
        """
        return self.filter(
            Q(sale_id=query) |
            Q(client__name__icontains=query) |
            Q(reference__icontains=query) |
            Q(notes__icontains=query) |
            Q(amount=query)
        )
    
    def for_client(self, client_id):
        """
        Filters records for a specific client id.
        """
        return self.filter(current_account__client_id=client_id)

    def newest(self):
        """Returns records ordered from newest to oldest."""
        return self.order_by('-created_at')

    def oldest(self):
        """Returns records ordered from oldest to newest."""
        return self.order_by('created_at')
    
    def total_amount(self):
        """
        Returns the total sum of the 'amount' field for the queryset.
        """
        return self.aggregate(total=Sum('amount'))['total'] or 0

    def credit_total(self):
        """
        Returns the total sum of credit movements.
        """
        return self.credit().total_amount()

    def debit_total(self):
        """
        Returns the total sum of debit movements.
        """
        return self.debit().total_amount()

    def effective(self):
        reversals = self.model.objects.filter(
            related_to=OuterRef('pk'),
            movement_type=MovementType.REVERSAL,
        )
        return (
            self.exclude(movement_type=MovementType.REVERSAL)
                .annotate(_has_reversal=Exists(reversals))
                .filter(_has_reversal=False)
        )

    def client_balance(self):
        net = Sum(
            Case(
                # Debe (ventas/cargos) -> restan
                When(movement_type=MovementType.DEBIT, then=-F('amount')),
                # A favor (pagos/devoluciones) -> suman
                When(movement_type__in=[MovementType.CREDIT, MovementType.REFUND], then=F('amount')),
                # Ajustes: dependen del original -> si corrige un DEBIT → suman; si corrige un CREDIT → restan
                When(Q(movement_type=MovementType.ADJUSTMENT) & Q(related_to__movement_type=MovementType.DEBIT), then=F('amount')),
                When(Q(movement_type=MovementType.ADJUSTMENT) & Q(related_to__movement_type=MovementType.CREDIT), then=-F('amount')),
                # cualquier otra cosa no suma
                default=Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        return self.aggregate(total=Coalesce(net, Value(Decimal('0.00'))))['total'] or Decimal('0.00')


class BalanceRecordsManager(Manager):
    def get_queryset(self):
        """
        Returns the custom queryset for account records.
        """
        return BalanceRecordsQueryset(self.model, using=self._db)
    
    def credit(self):
        """Returns all credit movements."""
        return self.get_queryset().credit()
    
    def debit(self):
        """Returns all debit movements."""
        return self.get_queryset().debit()
    
    def adjustment(self):
        """Returns all adjustment movements."""
        return self.get_queryset().adjustment()
    
    def refund(self):
        """Returns all refund movements."""
        return self.get_queryset().refund()
    
    def reversal(self):
        """Returns all reversal movements."""
        return self.get_queryset().reversal()
    
    def reconciled(self):
        """Returns all reconciled records."""
        return self.get_queryset().reconciled()
    
    def unreconciled(self):
        """Returns all unreconciled records."""
        return self.get_queryset().unreconciled()
    
    def with_related(self):
        """Returns records with related objects eagerly loaded."""
        return self.get_queryset().with_related()
    
    def with_related_records(self):
        """Returns records with related records eagerly loaded."""
        return self.get_queryset().with_related_records()
    
    def from_date(self, date):
        """Returns records from a given date (inclusive)."""
        return self.get_queryset().from_date(date)
    
    def to_date(self, date):
        """Returns records up to a given date (inclusive)."""
        return self.get_queryset().to_date(date)
    
    def search(self, query):
        """Performs a basic search on reference, client, or amount fields."""
        return self.get_queryset().search(query)
    
    def for_client(self, client_id):
        """Returns records for a specific client id."""
        return self.get_queryset().for_client(client_id)
    
    def newest(self):
        """Returns records ordered from newest to oldest."""
        return self.get_queryset().newest()
    
    def oldest(self):
        """Returns records ordered from oldest to newest."""
        return self.get_queryset().oldest()
    
    def total_amount(self):
        """Returns the total sum of the 'amount' field for all records."""
        return self.get_queryset().total_amount()
    
    def credit_total(self):
        """Returns the total sum of credit movements."""
        return self.get_queryset().credit_total()
    
    def debit_total(self):
        """Returns the total sum of debit movements."""
        return self.get_queryset().debit_total()

    def effective(self):
        return self.get_queryset().effective()

    def client_balance(self):
        return self.get_queryset().client_balance()
from django.db.models import Model
from django.db.models.fields import CharField, DecimalField, DateTimeField, BooleanField, TextField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import SET_NULL, PROTECT, CASCADE
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from decimal import Decimal

from cash.choices import SessionStatus, MovementType
from devices.models import CashRegister


class CashSession(Model):
    """Represents a cash register session (opening to closing)"""
    cash_register = ForeignKey(CashRegister, on_delete=PROTECT, related_name='sessions', verbose_name=_('cash register'))
    user = ForeignKey(get_user_model(), on_delete=PROTECT, related_name='cash_sessions', verbose_name=_('user'))
    
    status = CharField(max_length=20, choices=SessionStatus.choices, default=SessionStatus.OPEN, verbose_name=_('status'))
    
    opening_date = DateTimeField(auto_now_add=True, verbose_name=_('opening date'))
    closing_date = DateTimeField(null=True, blank=True, verbose_name=_('closing date'))
    
    opening_balance = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('opening balance'))
    closing_balance = DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name=_('closing balance'))
    
    notes = TextField(null=True, blank=True, verbose_name=_('notes'))
    
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('cash session')
        verbose_name_plural = _('cash sessions')
        ordering = ['-opening_date']

    def __str__(self):
        return f'{self.cash_register.name} - {self.user.get_full_name()} - {self.opening_date.strftime("%Y-%m-%d %H:%M")}'

    @property
    def total_cash_sales(self):
        """Calculate total sales in cash for this session"""
        from sales.models import Sale
        
        total = self.sales.filter(
            closed=True,
            canceled=False
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
        
        return total

    @property
    def total_cash_in(self):
        """Calculate total cash in movements (excluding opening)"""
        total = self.movements.filter(
            type=MovementType.CASH_IN
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        return total

    @property
    def total_cash_out(self):
        """Calculate total cash out movements (excluding closing)"""
        total = self.movements.filter(
            type=MovementType.CASH_OUT
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        return total

    @property
    def expected_balance(self):
        """Calculate the expected balance at closing"""
        return (
            self.opening_balance + 
            self.total_cash_sales + 
            self.total_cash_in - 
            self.total_cash_out
        )

    @property
    def difference(self):
        """Calculate difference between closing and expected balance"""
        if self.closing_balance is None:
            return Decimal('0.00')
        return self.closing_balance - self.expected_balance

    @property
    def sales_count(self):
        """Count of sales in this session"""
        return self.sales.filter(closed=True, canceled=False).count()

    def clean(self):
        """Validate before saving"""
        super().clean()
        
        # Validate opening balance is positive
        if self.opening_balance < 0:
            raise ValidationError({'opening_balance': _('Opening balance cannot be negative.')})
        
        # Validate branch access - user must be assigned to the branch
        if self.user and self.cash_register:
            # Check if cash register has a branch
            if hasattr(self.cash_register, 'branch') and self.cash_register.branch:
                # Check if user has branch assignments
                user_branches = self.user.branch.all()
                if user_branches.exists():
                    # User has branch assignments, verify they have access to this branch
                    if self.cash_register.branch not in user_branches:
                        raise ValidationError({
                            'user': _('User does not have access to this branch. User is assigned to: %(branches)s') % {
                                'branches': ', '.join([b.name for b in user_branches])
                            }
                        })
                # If user has no branch assignments, assume global access (allowed)
        
        # Validate only one open session per user
        if self.status == SessionStatus.OPEN and not self.pk:
            existing = CashSession.objects.filter(
                user=self.user,
                status=SessionStatus.OPEN
            ).exists()
            
            if existing:
                raise ValidationError({
                    'user': _('User already has an open cash session.')
                })
        
        # Validate only one open session per cash register
        if self.status == SessionStatus.OPEN and not self.pk:
            existing = CashSession.objects.filter(
                cash_register=self.cash_register,
                status=SessionStatus.OPEN
            ).exists()
            
            if existing:
                raise ValidationError({
                    'cash_register': _('This cash register already has an open session.')
                })
        
        # Validate closing balance when status is CLOSED
        if self.status == SessionStatus.CLOSED:
            if self.closing_balance is None:
                raise ValidationError({
                    'closing_balance': _('Closing balance is required when closing session.')
                })
            if self.closing_date is None:
                raise ValidationError({
                    'closing_date': _('Closing date is required when closing session.')
                })


class CashMovement(Model):
    """Represents a cash movement in a session (cash in/out)"""
    cash_session = ForeignKey(CashSession, on_delete=CASCADE, related_name='movements', verbose_name=_('cash session'))
    type = CharField(max_length=20, choices=MovementType.choices, verbose_name=_('type'))
    amount = DecimalField(max_digits=12, decimal_places=2, verbose_name=_('amount'))
    reason = CharField(max_length=200, verbose_name=_('reason'))
    description = TextField(null=True, blank=True, verbose_name=_('description'))
    created_by = ForeignKey(get_user_model(), on_delete=SET_NULL, null=True, verbose_name=_('created by'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))

    class Meta:
        verbose_name = _('cash movement')
        verbose_name_plural = _('cash movements')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()} - ${self.amount} - {self.reason}'

    def clean(self):
        """Validate before saving"""
        super().clean()
        
        # Validate positive amount
        if self.amount <= 0:
            raise ValidationError({'amount': _('Amount must be greater than zero.')})
        
        # Validate session is open (except for OPENING and CLOSING types)
        if self.type not in [MovementType.OPENING, MovementType.CLOSING]:
            if self.cash_session.status != SessionStatus.OPEN:
                raise ValidationError({
                    'cash_session': _('Cannot add movements to closed sessions.')
                })


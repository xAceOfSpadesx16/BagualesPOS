from __future__ import annotations
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Model, CASCADE, ManyToManyField
from django.db.models.fields import BooleanField, CharField, EmailField, DateTimeField
from django.db.models.fields.related import OneToOneField, ForeignKey
from django.utils.translation import gettext_lazy as _
from django_multitenant.models import TenantModel

from utils import PhoneNumberField



class CustomUser(AbstractUser):
    profile: Profile
    email = EmailField(null=True, verbose_name= _('email'))
    company = models.ForeignKey(
        'core.Company',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('company'),
        help_text=_('Company this user belongs to'),
        null=True,
        blank=True
    )
    branch = ManyToManyField(
        'core.Branch',
        blank=True,
        related_name='branch_users',
        verbose_name=_('branches'),
        help_text=_('Branches this user has access to')
    )
    
    # Override groups and user_permissions to avoid clashes with auth.User
    groups = ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='customuser_set',
        related_query_name='customuser',
    )
    user_permissions = ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customuser_set',
        related_query_name='customuser',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class Profile(Model):
    user = OneToOneField(get_user_model(), on_delete=CASCADE, related_name='profile', verbose_name= _('profile'))
    phone_number = PhoneNumberField(null=True, blank=True, verbose_name= _('phone number'))
    dni = CharField(max_length=9, null=True, blank=True, unique=True, verbose_name= _('dni'))
    address = CharField(max_length=100, null=True, blank=True, verbose_name= _('address'))
    city = CharField(max_length=50, null=True, blank=True, verbose_name= _('city'))
    province = CharField(max_length=50, null=True, blank=True, verbose_name= _('province'))
    postal_code = CharField(max_length=10, null=True, blank=True, verbose_name= _('postal code'))
    country = CharField(max_length=50, null=True, blank=True, verbose_name= _('country'))
    created_at = DateTimeField(auto_now_add=True, verbose_name= _('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name= _('updated at'))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')


class AuthorizationCode(TenantModel):
    """Codigos de autorizacion (escaneo de codigo de barras) para supervisores."""
    tenant_id = 'company_id'

    company = ForeignKey(
        'core.Company',
        on_delete=CASCADE,
        related_name='authorization_codes',
        verbose_name=_('company'),
        null=True,
        blank=True
    )
    user = ForeignKey(
        get_user_model(),
        on_delete=CASCADE,
        related_name='authorization_codes',
        verbose_name=_('user')
    )
    code = CharField(max_length=50, verbose_name=_('code'))
    label = CharField(max_length=100, verbose_name=_('label'))
    is_active = BooleanField(default=True, verbose_name=_('active'))
    created_at = DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    updated_at = DateTimeField(auto_now=True, verbose_name=_('updated at'))

    class Meta:
        verbose_name = _('authorization code')
        verbose_name_plural = _('authorization codes')
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'code'],
                name='unique_authorization_code_per_company'
            )
        ]

    def __str__(self) -> str:
        return f'{self.code} - {self.label}'
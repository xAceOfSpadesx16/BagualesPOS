from django.db import models
from django.utils.translation import gettext_lazy as _
from django_multitenant.models import TenantModel
from decimal import Decimal


class Company(TenantModel):
    """
    Represents a business entity (Tenant).
    Each company is isolated from others in a multi-tenant architecture.
    """
    tenant_id = 'id'
    
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Company name")
    )
    legal_name = models.CharField(
        _("legal name"),
        max_length=255,
        blank=True,
        default='',
        help_text=_("Legal name of the company")
    )
    address = models.CharField(
        _("address"),
        max_length=500,
        blank=True,
        default='',
        help_text=_("Company address")
    )
    phone = models.CharField(
        _("phone"),
        max_length=50,
        blank=True,
        default='',
        help_text=_("Company phone number")
    )
    email = models.EmailField(
        _("email"),
        max_length=255,
        blank=True,
        default='',
        help_text=_("Company email")
    )
    tax_id = models.CharField(
        _("tax ID"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Tax identification number (CUIT/RUT/etc.)")
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="companies/logos/",
        blank=True,
        null=True,
        help_text=_("Company logo")
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Whether this company is active")
    )
    owner = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.PROTECT,
        related_name='owned_company',
        verbose_name=_("owner"),
        help_text=_("User who owns this company"),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Branch(TenantModel):
    """
    Represents a physical location or division of a company.
    Branch data is isolated per tenant (company).
    """
    tenant_id = 'company_id'
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="branches",
        verbose_name=_("company"),
        help_text=_("Company this branch belongs to")
    )
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Branch name")
    )
    code = models.CharField(
        _("code"),
        max_length=50,
        help_text=_("Unique code for identifying this branch")
    )
    address = models.CharField(
        _("address"),
        max_length=500,
        blank=True,
        null=True,
        help_text=_("Physical address of the branch")
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Whether this branch is active")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("branch")
        verbose_name_plural = _("branches")
        ordering = ["company", "name"]
        unique_together = [["company", "code"]]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class CompanySettings(TenantModel):
    """Configuración global de la empresa."""
    tenant_id = 'company_id'

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='settings',
        verbose_name=_("company"),
    )

    # Tax
    tax_name = models.CharField(
        _("tax name"),
        max_length=50,
        blank=True,
        default='IVA',
        help_text=_("Nombre del impuesto (ej: IVA)")
    )
    tax_rate = models.DecimalField(
        _("tax rate"),
        max_digits=5,
        decimal_places=2,
        default=Decimal('21.00'),
        help_text=_("Porcentaje de impuesto")
    )
    tax_enabled = models.BooleanField(
        _("tax enabled"),
        default=True,
        help_text=_("Si el impuesto está activo")
    )

    # Currency
    currency_code = models.CharField(
        _("currency code"),
        max_length=3,
        default='ARS',
        help_text=_("Código de moneda ISO (ej: ARS, USD)")
    )
    currency_symbol = models.CharField(
        _("currency symbol"),
        max_length=5,
        default='$',
        help_text=_("Símbolo de moneda")
    )
    currency_decimals = models.PositiveSmallIntegerField(
        _("currency decimals"),
        default=2,
        help_text=_("Cantidad de decimales")
    )

    # Receipt
    receipt_header = models.TextField(
        _("receipt header"),
        blank=True,
        default='',
        help_text=_("Texto superior del ticket")
    )
    receipt_footer = models.TextField(
        _("receipt footer"),
        blank=True,
        default='',
        help_text=_("Texto inferior del ticket")
    )
    receipt_show_tax = models.BooleanField(
        _("receipt show tax"),
        default=True,
        help_text=_("Mostrar impuesto en el ticket")
    )

    # Stock
    allow_negative_stock = models.BooleanField(
        _("allow negative stock"),
        default=False,
        help_text=_("Permitir stock negativo")
    )
    low_stock_threshold = models.PositiveIntegerField(
        _("low stock threshold"),
        default=5,
        help_text=_("Umbral de stock bajo para alertas")
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("company settings")
        verbose_name_plural = _("company settings")

    def __str__(self):
        return f"Settings - {self.company.name}"

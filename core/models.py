from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """
    Represents a business entity.
    """
    name = models.CharField(
        _("name"),
        max_length=255,
        help_text=_("Company name")
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
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Branch(models.Model):
    """
    Represents a physical location or division of a company.
    """
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

from django.db.models.fields import BooleanField, DateTimeField
from django.forms import BoundField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden
from django.db import models
from rest_framework.viewsets import ViewSetMixin

# VIEWS MIXINS
class PatchMethodMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'patch':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        pass

class FormValidationMixin:
    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 422
        return response

class FetchRequestMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden(_("This view can only be accessed via Fetch."))
        return super().dispatch(request, *args, **kwargs)

# MODELS MIXINS

class SoftDeleteMixin(models.Model):
    is_deleted = BooleanField(_('deleted'), default=False)
    deleted_at = DateTimeField(_('deleted at'), null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = now()
        super().save(*args, **kwargs)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        super().save()

# DRF VIEWSET MIXINS

class TenantViewSetMixin:
    """
    Mixin que implementa el patrón estándar de filtrado multi-tenant
    para todos los ViewSets del proyecto.
    Jerarquía: superuser → owner (Admin General) → branch user.
    """
    company_field: str = 'company'
    branch_field: str = 'branch'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if getattr(self, 'swagger_fake_view', False):
            return queryset.model.objects.none()

        if not user.is_authenticated:
            return queryset.model.objects.none()

        if user.is_superuser:
            return queryset

        if hasattr(user, 'owned_company') and user.owned_company:
            return queryset.filter(**{self.company_field: user.owned_company})

        if hasattr(user, 'company') and user.company:
            user_branches = user.branch.all()
            if user_branches.exists():
                lookup = f'{self.branch_field}__in'
                return queryset.filter(**{lookup: user_branches})
            return queryset.filter(**{self.company_field: user.company})

        return queryset.model.objects.none()

    def get_user_company(self):
        """Retorna la company del usuario actual."""
        user = self.request.user
        if hasattr(user, 'owned_company') and user.owned_company:
            return user.owned_company
        if hasattr(user, 'company') and user.company:
            return user.company
        return None

    def get_user_branch(self):
        """Retorna la primera branch del usuario actual."""
        return self.request.user.branch.first()

    def is_admin(self):
        """Retorna True si el usuario es superuser o owner."""
        user = self.request.user
        return user.is_superuser or hasattr(user, 'owned_company')


# FORM MIXINS
class CustomBoundField(BoundField):
    def css_classes(self, extra_classes=None):
        return "form-group"


class FormGroupMixin:
    def __getitem__(self, name):
        return CustomBoundField(self, self.fields[name], name)

class RequiredSuffixMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label_suffix = ' *'
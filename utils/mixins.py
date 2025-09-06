from django.db.models.fields import BooleanField, DateTimeField
from django.forms import BoundField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden

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
class SoftDeleteMixin:
    is_deleted = BooleanField(_('deleted'), default=False)
    deleted_at = DateTimeField(_('deleted at'), null=True, blank=True)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = now()
        super().save(*args, **kwargs)

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
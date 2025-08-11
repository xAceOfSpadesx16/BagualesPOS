from django.db.models.fields import BooleanField, DateTimeField
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

# VIEWS MIXINS
class PatchMethodMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'patch':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        pass

class CreateFormValidationMixin:
    def form_valid(self, form):
        form.save()
        return JsonResponse({'redirect_url': self.success_url }, status = 200)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = 400
        return response
    
class UpdateFormValidationMixin:
    def form_valid(self, form):
        form.save()
        return JsonResponse({'redirect_url': self.success_url }, status = 200)

# MODELS MIXINS
class SoftDeleteMixin:
    is_deleted = BooleanField(_('deleted'), default=False)
    deleted_at = DateTimeField(_('deleted at'), null=True, blank=True)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = now()
        super().save(*args, **kwargs)
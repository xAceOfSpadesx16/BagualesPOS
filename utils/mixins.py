from django.db.models.fields import BooleanField, DateTimeField
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

class PatchMethodMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'patch':
            return self.patch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        pass

class SoftDeleteMixin(object):
    is_deleted = BooleanField(_('deleted'), default=False)
    deleted_at = DateTimeField(_('deleted at'), null=True, blank=True)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = now()
        super().save(*args, **kwargs)
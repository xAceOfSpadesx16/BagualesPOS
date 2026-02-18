from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from users.models import Profile, CustomUser


class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser to manage branch assignments"""
    
    fieldsets = UserAdmin.fieldsets + (
        (_('Branch Assignment'), {
            'fields': ('branch',),
            'description': _('Assign this user to specific branches. Leave empty for global access.')
        }),
    )
    
    filter_horizontal = ('branch', 'groups', 'user_permissions')
    
    list_filter = UserAdmin.list_filter + ('branch',)
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('branch')


# Register CustomUser with custom admin
admin.site.register(CustomUser, CustomUserAdmin)

# Register Profile
admin.site.register(Profile)


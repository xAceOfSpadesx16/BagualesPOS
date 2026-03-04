"""
Multi-tenant middleware for BagualesPOS.
Sets the current tenant based on the authenticated user's company.
"""
from django.utils.deprecation import MiddlewareMixin
from django_multitenant.utils import set_current_tenant
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to set the current tenant (company) for each request.
    
    This middleware extracts the company from the authenticated user
    and sets it as the current tenant for the request lifecycle.
    All queries will be automatically filtered by this tenant.
    """
    
    def process_request(self, request):
        user = request.user
        
        # If user is not authenticated natively (session/basic), try to authenticate via JWT
        # This is necessary because DRF processes authentication inside the view, NOT the middleware.
        # But we need the tenant context BEFORE the view.
        if not user or not user.is_authenticated:
            try:
                jwt_auth = JWTAuthentication()
                auth_result = jwt_auth.authenticate(request)
                if auth_result:
                    user, _ = auth_result
            except (InvalidToken, AuthenticationFailed):
                pass
                
        if user and user.is_authenticated:
            # Get the user's company
            if hasattr(user, 'company') and user.company:
                set_current_tenant(user.company)
        
        return None
    
    def process_response(self, request, response):
        """
        Clean up tenant context after request is processed.
        
        Args:
            request: The HTTP request object
            response: The HTTP response object
        """
        # Reset tenant context to None after request
        set_current_tenant(None)
        return response

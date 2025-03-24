# Create a new file in your project named middleware.py
from django.contrib.auth.views import redirect_to_login
from django.urls import resolve, reverse

class RequireLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check if the path requires auth
        path = request.path_info
        
        # Skip authentication for login page and admin
        if path.startswith('/accounts/login/') or path.startswith('/admin/'):
            return None
            
        # If user is not authenticated, redirect to login
        if not request.user.is_authenticated:
            resolved_login_url = reverse('login')
            return redirect_to_login(
                path, 
                resolved_login_url
            )
            
        return None
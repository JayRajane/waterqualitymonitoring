from django.contrib import admin
from django.urls import path, include
from monitoring_app.views import dashboard, CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),  # Custom login view
    path('accounts/', include('django.contrib.auth.urls')),  # Other auth URLs (logout, etc.)
    path('', dashboard, name='home'),
    path('', include('monitoring_app.urls')),
]
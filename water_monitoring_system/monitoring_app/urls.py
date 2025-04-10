from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'water-quality', views.WaterQualityDataViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.dashboard, name='dashboard'),
    path('all-users/', views.all_users_dashboard, name='all_users_dashboard'),
    path('live-status/<int:user_id>/', views.live_status, name='live_status'),
    path('download/<int:user_id>/', views.download_page, name='download_page'),
    path('download-data/<int:user_id>/', views.download_data, name='download_data'),
    path('download-credentials/<int:user_id>/', views.download_user_credentials, name='download_user_credentials'),
    path('add-data/', views.add_data, name='add_data'),
    path('data-entry/', views.data_entry, name='data_entry'),
    path('submit-data/', views.submit_data, name='submit_data'),
    path('user-management/', views.user_management, name='user_management'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('accounts/logout/', views.logout_confirm, name='logout'),
]
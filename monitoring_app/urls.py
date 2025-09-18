from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from monitoring_app import views

router = DefaultRouter()
router.register(r'water-quality', views.WaterQualityDataViewSet)
router.register(r'readings', views.ReadingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Explicitly define latest endpoints for clarity
    path('api/water-quality/latest/', views.WaterQualityDataViewSet.as_view({'get': 'latest'}), name='water-quality-latest'),
    path('api/readings/latest/', views.ReadingViewSet.as_view({'get': 'latest'}), name='readings-latest'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/all-users/', views.all_users_dashboard, name='all_users_dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('calibrate-flow/<int:user_id>/', views.calibrate_flow, name='calibrate_flow'),
    path('fetch-external-flow/<int:user_id>/', views.fetch_external_flow, name='fetch_external_flow'),
    path('download-credentials/<int:user_id>/', views.download_user_credentials, name='download_user_credentials'),
    path('logout-confirm/', views.logout_confirm, name='logout_confirm'),
    path('live-status/<int:user_id>/', views.live_status, name='live_status'),
    path('download/<int:user_id>/', views.download_page, name='download_page'),
    path('download-data/<int:user_id>/', views.download_data, name='download_data'),
    path('preview-data/<int:user_id>/', views.preview_data, name='preview_data'),
    path('add-data/', views.add_data, name='add_data'),
    path('data-entry/', views.data_entry, name='data_entry'),
    path('submit-data/', views.submit_data, name='submit_data'),
    path('water-analyzer/', views.water_analyzer_dashboard, name='water_analyzer_dashboard'),
    path('calibration-status/', views.calibration_status, name='calibration_status'),
    path('reset-calibration/', views.reset_calibration, name='reset_calibration'),
    path('submit-data/', views.submit_data, name='submit_data'),
    path('water-analyzer/', views.water_analyzer_dashboard, name='water_analyzer_dashboard'),
    path('api/external-data/', views.get_external_data, name='get_external_data'),
    path('analyzer/', views.water_analyzer_dashboard, name='water_analyzer_dashboard'),
    path('analyzer/<int:user_id>/', views.water_analyzer_dashboard, name='water_analyzer_dashboard_with_user'),
    

    path('api/external-data/', views.get_external_data, name='get_external_data'),
    path('api/users/', views.get_users_list, name='get_users_list'),
    path('submit-data/', views.submit_data, name='submit_data'),
    path('calibration-status/', views.calibration_status, name='calibration_status'),
    path('reset-calibration/', views.reset_calibration, name='reset_calibration'),
]
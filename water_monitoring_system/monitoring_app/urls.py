from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'water-quality', views.WaterQualityDataViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Web URLs
    path('', views.dashboard, name='dashboard'),
    path('live-status/<int:user_id>/', views.live_status, name='live_status'),
    path('download/<int:user_id>/', views.download_page, name='download_page'),
    path('download-data/<int:user_id>/', views.download_data, name='download_data'),
    path('add-data/', views.add_data, name='add_data'),
    path('data-entry/', views.data_entry, name='data_entry'),
    path('submit-data/', views.submit_data, name='submit_data'),
    path('api/users/', views.user_list, name='user_list'),
    path('api/water-qualitys/', views.water_quality_data, name='water_quality_data'),




]
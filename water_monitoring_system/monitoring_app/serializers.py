from rest_framework import serializers
from .models import WaterQualityData
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class WaterQualityDataSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = WaterQualityData
        fields = ['id', 'user', 'username', 'timestamp', 'ph', 'flow', 'total_flow', 
                  'cod', 'bod', 'tss', 'daily_flow', 'date']
        read_only_fields = ['daily_flow', 'date']